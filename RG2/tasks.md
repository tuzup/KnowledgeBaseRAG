Phase 1: Infrastructure & Database Setup
[ ] PostgreSQL Initialization

[ ] Install PostgreSQL 15+ and enable pgvector extension (CREATE EXTENSION vector;).

[ ] Create the knowledge_sources table with columns for app_name, category, and confluence_parent_id.

[ ] Create the knowledge_chunks table with:

[ ] embedding column set to vector(1024) (Optimized text-embedding-3-large).

[ ] linked_text_chunk_id (UUID) and linked_image_chunk_ids (UUID[]) columns.

[ ] content column (TEXT) to hold both text and VLM descriptions.

[ ] Create HNSW index on the embedding column for fast retrieval.

[ ] Create B-Tree indexes on app_name, category, and chunk_type for filtering.

[ ] Project Structure

[ ] Initialize Node.js project (npm init) with Express/NestJS.

[ ] Initialize Python project (poetry init or pip) with FastAPI.

[ ] Set up shared .env file structure (OpenAI Keys, DB URL, Confluence Creds).

Phase 2: Python Engine (FastAPI) - The "Worker"
[ ] Core Setup

[ ] Install dependencies: docling, beautifulsoup4, psycopg[binary], openai, fastapi, uvicorn.

[ ] Create database.py with the PostgresVectorConnector class (connection pooling, batch insert).

[ ] PDF Processing (/process/pdf)

[ ] Implement DocumentProcessor class using Docling + HybridChunker.

[ ] Implement logic to extract images from PDF using Docling's PictureItem.

[ ] Implement _annotate_image using OpenAI GPT-4o (or similar VLM).

[ ] Linking Logic: Ensure text_chunk_uuid is injected into the Image Chunk's linked_text_chunk_id field during the loop.

[ ] Confluence Processing (/process/confluence)

[ ] Implement ConfluenceFetcher to get HTML content by Page ID.

[ ] Rate Limit Handler: Implement the time.sleep loop or a task queue (Celery/BackgroundTasks) for recursive sub-page fetching.

[ ] HTML Parser:

[ ] Use BeautifulSoup to find <img> tags and download them to local disk/S3.

[ ] Create a map: PictureItem Ref -> Local Path.

[ ] Use Docling to parse the cleaned HTML text.

[ ] Match Docling's detected pictures to your downloaded local paths using the "Parallel Alignment" strategy.

[ ] Embedding & Storage

[ ] Implement generate_embedding using text-embedding-3-large with dimensions=1024.

[ ] Create upsert_chunks function that writes to knowledge_chunks with correct app_name and category.

[ ] Search & Retrieval (/query)

[ ] Implement search_knowledge endpoint.

[ ] Add logic to filter by app_name using PostgreSQL ANY operator.

[ ] Expansion Logic: If an Image Chunk is found, fetch its parent Text Chunk (and vice versa) using the linked UUIDs.

Phase 3: Node.js Orchestrator (Backend)
[ ] API Gateway Setup

[ ] Create POST /api/upload (Multer for file handling).

[ ] Create POST /api/confluence (Accepts Page ID & Credentials/Token).

[ ] Create POST /api/chat (Accepts User Query).

[ ] Orchestration Logic

[ ] Upload: Save file to temp disk -> Call Python /process/pdf.

[ ] Confluence: Validate request -> Call Python /process/confluence (Async).

[ ] Chat:

[ ] Call Python /query to get relevant chunks.

[ ] Token Injection: Map retrieved images to {{IMG_1}}, {{IMG_2}} tokens.

[ ] Context Building: Inject [VISUAL ASSET: {{IMG_1}} ...] directly into the text context string.

[ ] LLM Call: Send System Prompt + Context to OpenAI (GPT-4).

[ ] Post-Processing: Regex replace {{IMG_X}} with real static URLs (e.g., http://localhost:3000/static/...).

Phase 4: Frontend (React)
[ ] Knowledge Management UI

[ ] Create "Upload Document" form (File Picker + App Name dropdown).

[ ] Create "Add Confluence Page" form (URL input + Subpages checkbox).

[ ] Create "Knowledge List" table (Fetch from Node.js GET /api/documents).

[ ] Chat Interface

[ ] Build Chat Window (User Message vs. AI Response).

[ ] Markdown Rendering: Install react-markdown.

[ ] Image Support: Ensure the markdown renderer correctly handles standard ![alt](url) syntax (which Node.js will have generated).

[ ] Add "Sources" section below the answer to list knowledge_sources.title used.

Phase 5: Verification & Testing
[ ] Test Linking: Manually check the DB to ensure an Image Chunk has a valid linked_text_chunk_id that points to a real Text Chunk.

[ ] Test Confluence Images: Run the pipeline on a Confluence page with an image. Verify the image is saved to your images/ folder and the description is in the DB.

[ ] Test Multi-App Search:

[ ] Search "Policy" with app_name=['HR'] -> Should return HR docs.

[ ] Search "Policy" with app_name=['IT'] -> Should return IT docs (or nothing).

[ ] Test Visual Q&A: Ask "Show me the architecture diagram." Verify the LLM outputs the image in the chat.