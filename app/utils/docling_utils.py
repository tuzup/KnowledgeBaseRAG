"""
Docling utility functions.
"""
from pathlib import Path
from docling_core.types.doc import PictureItem, TableItem

def save_image_ref(conv_res, output_path: str, filename: str, replace_blank: str = "_"):
    """ Save image references from document conversion result."""
    print(f"Saving image references to {output_path}")
    output_dir = Path(output_path)
    filename_sanitized = filename.strip() or replace_blank
    doc_dir = output_dir / filename_sanitized
    doc_dir.mkdir(parents=True, exist_ok=True)

    picture_counter = 0
    table_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = doc_dir / f"table-{table_counter}.png"
            try:
                with element_image_filename.open("wb") as fp:
                    element.get_image(conv_res.document).save(fp, "PNG")
                print(f"Saved table image: {element_image_filename}")
            except Exception as e:
                print(f"Error saving table image: {e}")

        if isinstance(element, PictureItem):
            print(f"element: {element}")
            picture_counter += 1
            element_image_filename = doc_dir / f"picture-{picture_counter}.png"
            try:
                with element_image_filename.open("wb") as fp:
                    element.get_image(conv_res.document).save(fp, "PNG")
                print(f"Saved picture image: {element_image_filename}")
            except Exception as e:
                print(f"Error saving picture image: {e}")

    print(f"Saved {picture_counter} pictures and {table_counter} tables")


