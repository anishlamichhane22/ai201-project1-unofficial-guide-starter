"""Embed professor-review chunks and provide semantic retrieval.

Loads chunks from ingest.py, embeds them with the all-MiniLM-L6-v2
sentence-transformer, stores them in an in-memory ChromaDB collection,
and exposes a retrieve() function for top-k semantic search.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import load_and_chunk_documents

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "professor_reviews"

# Load the embedding model and build the collection once at import time so
# that app.py can simply call retrieve() without re-indexing per request.
_model = SentenceTransformer(MODEL_NAME)
_client = chromadb.Client()


def _build_collection():
    """(Re)create the Chroma collection and index all chunks."""
    # Start from a clean collection so repeated runs don't duplicate data.
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = _client.create_collection(COLLECTION_NAME)

    chunks = load_and_chunk_documents()
    if not chunks:
        print("No chunks to embed — check the data/ folder.")
        return collection

    texts = [c["text"] for c in chunks]
    embeddings = _model.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=[f"{c['source']}-{c['chunk_index']}" for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {"source": c["source"], "chunk_index": c["chunk_index"]}
            for c in chunks
        ],
    )

    print(f"Embedded and stored {len(chunks)} chunks in ChromaDB.")
    return collection


_collection = _build_collection()


def retrieve(query, top_k=4):
    """Return the top_k most relevant chunks for a query string.

    Each result is a dict with keys: source, chunk_index, text, distance.
    """
    query_embedding = _model.encode([query]).tolist()
    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "text": doc,
            "distance": dist,
        }
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]


def main():
    test_queries = [
        "What do students say about Antunez?",
        "How difficult are Dr. Primo's exams?",
        "Is web programming a good course?",
    ]

    for query in test_queries:
        print("=" * 70)
        print(f"Query: {query}")
        print("=" * 70)
        for i, result in enumerate(retrieve(query), start=1):
            print(f"{i}. [{result['source']} #{result['chunk_index']}] "
                  f"(distance={result['distance']:.4f})")
            print(f"   {result['text']}")
        print()


if __name__ == "__main__":
    main()
