"""
Image extraction utilities.
"""
from pathlib import Path
import re
from celery import uuid
from docling_core.types.doc import DocItemLabel
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

def get_image_info(doc, chunk, image_dir_path: str) -> dict:
    """Get image information from a document chunk."""
    picture_lookup = {item.self_ref: item for item in doc.pictures}
    table_lookup = {item.self_ref: item for item in doc.tables}
    image_dir_path.mkdir(parents=True, exist_ok=True)
    image_info = {
        "has_images": False,
        "figures": [],
        "tables": []
    }

    try:
        encountered_refs = set()
        for doc_item_ref in chunk.meta.doc_items:
            ref = doc_item_ref.self_ref
            target_item = None

            if ref in picture_lookup:
                target_item = picture_lookup[ref]
            elif ref in table_lookup:
                target_item = table_lookup[ref]
            
            if target_item and target_item.self_ref not in encountered_refs:
                encountered_refs.add(target_item.self_ref)
                # Safely get page number
                page_no = target_item.prov[0].page_no if target_item.prov and len(target_item.prov) > 0 else 0
                # Safely get caption text
                caption_text = "No caption"
                if hasattr(target_item, 'caption') and target_item.caption and hasattr(target_item.caption, 'text'):
                    caption_text = target_item.caption.text

                # --- Handle Pictures ---
                if isinstance(target_item, PictureItem):
                    fig_id = uuid.uuid4().hex[:8]
                    image_info["has_images"] = True
                    print(f"Found picture item on page {page_no} with caption: {caption_text}")
                    image_filename = f"p{page_no}_{fig_id}.png"
                    image_path = image_dir_path / image_filename
                    try:
                        with image_path.open("wb") as fp:
                            target_item.get_image(doc).save(fp, "PNG")
                        image_info["figures"].append({
                                "image_url": str(image_path), 
                                "caption": caption_text,
                                "page_no": page_no,
                                "type": "figure"
                            })
                        print(f"Saved picture image: {image_path}")
                    except Exception as e:
                        print(f"Error saving picture image: {e}")
                    
    except Exception as e:
        print(f"Error extracting image info: {e}")
    
    return image_info



def extract_image_info_from_chunk(chunk, filename: str, chunk_idx: int, image_dir_path: str, picture_counter: int = 0, table_counter: int = 0, replace_blank: str = "_") -> dict:
    """Extract image information from a document chunk."""

    output_dir = Path(image_dir_path)
    # sanitize filename and create a folder for this document
    filename_sanitized = filename.strip() or replace_blank
    image_dir = output_dir / filename_sanitized
    image_dir.mkdir(parents=True, exist_ok=True) 

    image_info = {
        "has_images": False,
        "image_count": 0,
        "image_references": "",
        "image_descriptions": "",
        "figure_captions": "",
        "table_count": 0,
    }

    try:
        image_refs = []
        descriptions = []
        captions = []

        # Check document items
        for item in chunk.meta.doc_items:
            if item.label == DocItemLabel.PICTURE:
                picture_counter += 1
                image_info["has_images"] = True
                img_ref = f"{image_dir}/picture-{picture_counter}.png"
                image_refs.append(img_ref)

            elif item.label == DocItemLabel.TABLE:
                table_counter += 1
                image_info["has_images"] = True
                img_ref = f"{image_dir}/table-{table_counter}.png"
                image_refs.append(img_ref)

            elif item.label == DocItemLabel.CAPTION:
                if item.prov:
                    for prov in item.prov:
                        if hasattr(prov, 'charspan') and prov.charspan:
                            start, end = prov.charspan
                            caption_text = chunk.text[start:end] if start < len(chunk.text) else ""
                            if caption_text.strip():
                                captions.append(caption_text.strip())
                                break

        # Check markdown images
        markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', chunk.text)
        if markdown_images:
            for alt_text, img_path in markdown_images:
                image_info["has_images"] = True
                picture_count += 1
                image_refs.append(img_path)
                if alt_text:
                    descriptions.append(alt_text)

        # Update counts
        image_info["image_references"] = "|".join(image_refs) if image_refs else ""
        image_info["image_descriptions"] = "|".join(descriptions) if descriptions else ""
        image_info["figure_captions"] = "|".join(captions) if captions else ""

    except Exception as e:
        print(f"Error extracting image info: {e}")

    return image_info, picture_counter, table_counter
