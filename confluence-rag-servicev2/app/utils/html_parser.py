import uuid
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.core.config import settings

class HtmlProcessor:
    def __init__(self, base_url):
        self.base_url = base_url
        self.images = []

    def process(self, html_content, page_id, page_title):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Iterate all images
        for i, img in enumerate(soup.find_all('img')):
            src = img.get('src')
            if not src: continue
            
            # 1. Prepare Metadata
            filename = f"img_{page_id}_{i:03d}.png"
            full_url = urljoin(self.base_url, src)
            chunk_id = f"image_{uuid.uuid4().hex[:8]}"
            
            # 2. Extract Context (Ported from your test.py _get_image_context)
            context = self._get_image_context(img)
            
            # 3. Build Image Chunk (Matching test.py schema)
            self.images.append({
                "chunk_type": "image",
                "chunk_id": chunk_id,
                "filename": filename,
                "image_url": full_url,
                "local_path": str(settings.OUTPUT_DIR / "images" / filename),
                "context_text": context,
                # The exact LLM prompt format from test.py
                "llm_prompt": f'Describe this technical image/diagram in detail.\nContext from surrounding text: "{context[:150]}..."\nFocus on charts, diagrams, code, technical content.',
                "llm_description": None,
                "text_refs": [],
                "metadata": {
                    "page_id": page_id,
                    "original_src": src
                }
            })
            
            # 4. Inject Marker (Upgrade from heuristic linking)
            # Replaces <img> with [[IMG:ID]] so Docling preserves location
            img.replace_with(f" [[IMG:{chunk_id}]] ")
            
        return str(soup)

    def _get_image_context(self, img_tag) -> str:
        """Exact port of test.py logic"""
        context_parts = []
        
        # Previous text
        prev = img_tag.find_previous_sibling(['p', 'div', 'span', 'h1', 'h2', 'li'])
        if prev: context_parts.append(prev.get_text(strip=True)[:200])
        
        # Next text
        nxt = img_tag.find_next_sibling(['p', 'div', 'span', 'h1', 'h2', 'li'])
        if nxt: context_parts.append(nxt.get_text(strip=True)[:200])
        
        # Parent container
        parent = img_tag.find_parent(['figure', 'figcaption', 'div'])
        if parent and parent != img_tag.parent:
            caption = parent.get_text(strip=True)[:200]
            if caption: context_parts.append(caption)
            
        # Alt/Title
        if img_tag.get('alt'): context_parts.append(img_tag['alt'])
        
        return " ".join(context_parts)[:500]