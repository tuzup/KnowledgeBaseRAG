"""
Document processing service.
"""
import os
import hashlib
import logging
from typing import List, Optional, Tuple
from pathlib import Path

from openai import OpenAI
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, PictureDescriptionApiOptions
from docling.datamodel.base_models import InputFormat
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
from docling_core.types.doc import PictureItem, TableItem, DocItemLabel
from docling_core.types.doc.document import ImageRefMode
import tiktoken

from app.core.config import settings
from app.utils.docling_utils import save_image_ref
from app.utils.image_utils import extract_image_info_from_chunk, get_image_info

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing documents with Docling."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.tokenizer = OpenAITokenizer(
            tokenizer=tiktoken.encoding_for_model("gpt-4o"),
            max_tokens=128 * 1024,
        )
        self.converter = self._initialize_converter()

    def _initialize_converter(self) -> DocumentConverter:
        """Initialize Docling document converter."""
        pipeline_options = PdfPipelineOptions(
            do_picture_description=True,
            picture_description_options=PictureDescriptionApiOptions(
                url="https://api.openai.com/v1/chat/completions",
                prompt="Describe this image in detail, including any text, charts, diagrams, or visual elements.",
                params=dict(model=settings.OPENAI_MODEL),
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                timeout=settings.PICTURE_DESCRIPTION_TIMEOUT,
            ),
            enable_remote_services=True,
            generate_picture_images=True,
            generate_table_images=True,
            generate_page_images=True,
            images_scale=settings.IMAGES_SCALE,
        )

        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def process_pdf(
        self,
        pdf_path_or_url: str,
        category: str,
        subcategory: Optional[str] = None
    ) -> Tuple[List[str], List[dict], List[str]]:
        """
        Process a PDF document.

        Args:
            pdf_path_or_url: Path or URL to PDF
            category: Document category
            subcategory: Optional subcategory

        Returns:
            Tuple of (texts, metadatas, ids)
        """
        logger.info(f"Converting PDF: {pdf_path_or_url}")
        result = self.converter.convert(pdf_path_or_url)

        # Extract filename and document ID
        if pdf_path_or_url.startswith(('http://', 'https://')):
            filename = pdf_path_or_url.split('/')[-1]
        else:
            filename = Path(pdf_path_or_url).name

        doc_id = hashlib.md5(pdf_path_or_url.encode()).hexdigest()[:8]

        # Save images 
        # save_image_ref(result, settings.OUTPUT_DIR, filename)
        

        # Chunk the document
        chunker = HybridChunker(
            tokenizer=self.tokenizer,
            max_tokens=settings.CHUNKING_MAX_TOKENS,
            merge_peers=True,
        )
        chunks = list(chunker.chunk(dl_doc=result.document))

        # Count images and tables
        total_pictures = sum(
            1 for element, _ in result.document.iterate_items()
            if isinstance(element, PictureItem)
        )
        total_tables = sum(
            1 for element, _ in result.document.iterate_items()
            if isinstance(element, TableItem)
        )

        logger.info(
            f"Document contains {total_pictures} pictures and {total_tables} tables"
        )

        # Process chunks
        processed_texts = []
        metadatas = []
        ids = []
        # picture_counter = 0
        # table_counter = 0

        for i, chunk in enumerate(chunks):
            text = chunk.text
            image_info = get_image_info(result.document, chunk, Path(settings.OUTPUT_DIR / filename))
            # image_info, picture_counter, table_counter = extract_image_info_from_chunk(result, chunk, filename, i, settings.OUTPUT_DIR, picture_counter, table_counter)

            # Extract page numbers
            try:
                page_numbers = sorted(
                    set(
                        prov.page_no
                        for item in chunk.meta.doc_items
                        for prov in item.prov
                        if hasattr(prov, 'page_no') and prov.page_no is not None
                    )
                )
                page_numbers_str = ",".join(map(str, page_numbers)) if page_numbers else ""
            except Exception:
                page_numbers_str = ""

            # Extract title
            try:
                title = chunk.meta.headings[0] if chunk.meta.headings else ""
            except Exception:
                title = ""

            metadata = {
                "filename": filename,
                "document_id": doc_id,
                "category": category,
                "subcategory": subcategory or "",
                "page_numbers": page_numbers_str,
                "title": title,
                "source_path": pdf_path_or_url,
                "has_images": image_info["has_images"],
                "image_count": image_info["image_count"],
                "table_count": image_info["table_count"],
                "image_references": image_info["image_references"],
                "image_descriptions": image_info["image_descriptions"],
                "figure_captions": image_info["figure_captions"],
            }

            processed_texts.append(text)
            metadatas.append(metadata)
            ids.append(f"{doc_id}-chunk-{i}")

        return processed_texts, metadatas, ids
