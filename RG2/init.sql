-- Enable vector support
CREATE EXTENSION IF NOT EXISTS vector;

-- Define the Status Enum Type first
-- This creates a custom data type in Postgres that accepts only these values.
CREATE TYPE source_status AS ENUM ('pending', 'processing', 'active', 'error');

CREATE TABLE knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 1. Tenant/App Isolation
    app_name VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- 2. Source Metadata
    title TEXT NOT NULL,
    source_type VARCHAR(20) CHECK (source_type IN ('pdf', 'confluence')),
    source_path TEXT, -- Original input path (S3 URL or Confluence Link)
    
    -- 3. Confluence Specifics
    confluence_page_id TEXT,
    confluence_parent_id TEXT,
    
    -- 4. Pipeline Status Tracking (Using ENUM)
    status source_status DEFAULT 'pending',
    error_message TEXT,
    
    -- 5. Operational Data (NEW FIELDS)
    -- Critical path where processed assets (images) are stored on disk/S3.
    -- e.g., "./processed_data/doc_uuid_123/"
    output_directory TEXT, 
    
    -- Informational stats about the processing job results.
    -- Example data structure: 
    -- { 
    --   "total_chunks": 45, 
    --   "total_images": 12, 
    --   "pdf_page_count": 25,
    --   "processing_time_sec": 14.5
    -- }
    processing_stats JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_sources_app_cat ON knowledge_sources(app_name, category);
-- Optional: GIN index on stats if you ever plan to search inside the JSON
-- CREATE INDEX idx_sources_stats ON knowledge_sources USING GIN (processing_stats);


CREATE TABLE knowledge_chunks (
    -- Primary Key MUST be provided by the application (Python) during insertion
    id UUID PRIMARY KEY, 
    
    -- Link to parent source. Delete source -> Delete all its chunks automatically.
    source_id UUID NOT NULL REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    
    -- 1. Fast Filtering Columns (Denormalized for speed)
    app_name VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    chunk_type VARCHAR(10) CHECK (chunk_type IN ('text', 'image')),
    
    -- 2. Core Content & Vector
    content TEXT NOT NULL, -- Raw text OR VLM image description
    embedding vector(1024), -- Optimized dimension for text-embedding-3-large
    
    -- 3. Image Specifics
    image_path TEXT, -- Relative path to the actual image file inside output_directory
    
    -- 4. Bi-Directional Linking
    linked_text_chunk_id UUID,       
    linked_image_chunk_ids UUID[],
    
    -- 5. Contextual Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes used for RAG search and filtering
CREATE INDEX idx_chunks_embedding ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_filters ON knowledge_chunks (app_name, category, chunk_type);
CREATE INDEX idx_chunks_source ON knowledge_chunks (source_id);