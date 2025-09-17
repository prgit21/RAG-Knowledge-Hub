CREATE EXTENSION IF NOT EXISTS vector;

-- Ensure HNSW indexes exist for cosine similarity searches; PostgreSQL keeps them
-- synchronized automatically as data is inserted or updated.
CREATE INDEX IF NOT EXISTS embeddings_embedding_hnsw_idx
    ON embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS images_embedding_hnsw_idx
    ON images USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS images_text_embedding_hnsw_idx
    ON images USING hnsw (text_embedding vector_cosine_ops);
