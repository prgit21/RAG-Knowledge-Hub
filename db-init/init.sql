CREATE EXTENSION IF NOT EXISTS vector;

-- Ensure HNSW indexes exist for cosine similarity searches; PostgreSQL keeps them
-- synchronized automatically as data is inserted or updated. They must be created
-- concurrently so inserts continue to flow while PostgreSQL builds the index.
--
-- The \gexec meta-command is used so the CREATE INDEX statements only run when the
-- index is missing. Each command is executed outside an explicit transaction so the
-- CONCURRENTLY clause is allowed.
SELECT 'CREATE INDEX CONCURRENTLY embeddings_embedding_hnsw_idx '
       'ON embeddings USING hnsw (embedding vector_cosine_ops)'
WHERE to_regclass('embeddings_embedding_hnsw_idx') IS NULL
\gexec

SELECT 'CREATE INDEX CONCURRENTLY images_embedding_hnsw_idx '
       'ON images USING hnsw (embedding vector_cosine_ops)'
WHERE to_regclass('images_embedding_hnsw_idx') IS NULL
\gexec

SELECT 'CREATE INDEX CONCURRENTLY images_text_embedding_hnsw_idx '
       'ON images USING hnsw (text_embedding vector_cosine_ops)'
WHERE to_regclass('images_text_embedding_hnsw_idx') IS NULL
\gexec
