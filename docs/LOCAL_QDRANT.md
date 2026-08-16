# Local Qdrant Setup

OmniBrain uses Qdrant for document and image vector retrieval.

## Start Qdrant

Run Qdrant locally using Docker:

docker run -d --name omnibrain-qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant

## Verify Qdrant

Check the running container:

docker ps

Check the Qdrant API:

Invoke-RestMethod "http://localhost:6333/collections"

## Collections

The application uses:

- omnibrain_documents for document embeddings
- omnibrain_images for image embeddings

## Local RAG Testing

A newly started Qdrant instance is empty. Documents must be ingested before /query can retrieve document context.

The API runs at:

http://127.0.0.1:8000

The query endpoint is:

POST /query