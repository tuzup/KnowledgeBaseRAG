import re
import logging
from app.core.config import settings
from app.services.confluence import ConfluenceClient
from app.utils.html_parser import HtmlProcessor
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

logger = logging.getLogger("pipeline")

class RAGPipeline:
    def __init__(self, req):
        self.req = req
        self.client = ConfluenceClient(req.url, req.username, req.token)
        self.converter = DocumentConverter(allowed_formats=[InputFormat.HTML])

    def run(self):
        # 1. Root ID Extraction
        base_url = f"{self.req.url.split('/wiki/')[0]}/wiki"
        match = re.search(r'pages/(\d+)', self.req.url)
        if not match: raise ValueError("Invalid Confluence URL")
        root_id = match.group(1)
        
        # 2. Stack-Based Traversal (Handles max_depth=-1)
        # Tuple: (page_id, depth, parent_title) -> Metadata Requirement
        stack = [(root_id, 0, "ROOT")] 
        all_chunks = []
        processed_pages = 0
        
        print(f"🚀 Starting Traversal (Recursive={self.req.recursive}, Depth={self.req.max_depth})")
        
        while stack:
            page_id, depth, parent_title = stack.pop(0)
            
            # Check Depth
            if self.req.max_depth != -1 and depth > self.req.max_depth:
                continue
                
            # A. Fetch (1 API Call)
            print(f"📄 [{depth}] Processing {page_id}...")
            data = self.client.get_page_with_children(page_id)
            if not data: continue
            
            title = data['title']
            space_key = data.get('space', {}).get('key', 'UNKNOWN')
            page_url = f"{base_url}/spaces/{space_key}/pages/{page_id}"
            
            # B. Process HTML & Images
            processor = HtmlProcessor(base_url)
            clean_html = processor.process(data['body']['storage']['value'], page_id, title)
            
            # C. Docling Chunking
            page_chunks = self._chunk_content(clean_html, processor.images, page_id, title, page_url, depth, parent_title)
            all_chunks.extend(page_chunks)
            processed_pages += 1
            
            # D. Handle Children
            if self.req.recursive:
                children = data.get('children', {}).get('page', {}).get('results', [])
                print(f"  📂 Found {len(children)} children")
                for child in children:
                    # Pass current title as parent_title to children
                    stack.append((child['id'], depth + 1, title))
        
        return {
            "total_chunks": len(all_chunks),
            "pages_processed": processed_pages,
            "chunks": all_chunks
        }

    def _chunk_content(self, html, images, page_id, title, url, depth, parent_title):
        # Save temp HTML (Docling requirement)
        temp_path = settings.OUTPUT_DIR / "html" / f"{page_id}.html"
        temp_path.write_text(html, encoding="utf-8")
        
        # Docling Conversion
        doc = self.converter.convert(temp_path).document
        
        final_chunks = []
        
        # 1. Text Chunks
        for item, level in doc.iterate_items():
            text = item.text.strip()
            if not text: continue
            
            # Detect Markers [[IMG:ID]]
            img_refs = re.findall(r'\[\[IMG:(image_[a-f0-9]+)\]\]', text)
            clean_text = re.sub(r'\[\[IMG:image_[a-f0-9]+\]\]', '', text).strip()
            
            if not clean_text and not img_refs: continue
            
            chunk_id = f"text_{len(final_chunks)}_{page_id}"
            
            # EXACT Metadata Schema from test.py
            final_chunks.append({
                "chunk_type": "text",
                "chunk_id": chunk_id,
                "content": clean_text,
                "image_ref": img_refs[0] if img_refs else None, # Compatibility with test.py single ref
                "all_image_refs": img_refs, # Enhancement
                "page_metadata": {
                    "page_id": page_id,
                    "page_title": title,
                    "parent_title": parent_title,
                    "page_url": url,
                    "page_depth": depth,
                    "char_count": len(clean_text)
                }
            })
            
            # Bidirectional Link Backfill
            for ref in img_refs:
                for img in images:
                    if img['chunk_id'] == ref:
                        img['text_refs'].append(chunk_id)

        # 2. Image Chunks (Download & Finalize)
        for img in images:
            self.client.download_image(img['image_url'], img['local_path'])
            # Add Page Metadata to Image Chunk too
            img['page_metadata'] = {
                "page_id": page_id,
                "page_title": title,
                "parent_title": parent_title,
                "page_url": url,
                "page_depth": depth
            }
            final_chunks.append(img)
            
        return final_chunks