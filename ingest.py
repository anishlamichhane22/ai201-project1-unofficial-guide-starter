"""Ingest professor reviews from Huston-Tillotson University.

Loads .txt files from the data/ folder, cleans the text, and splits each
document into overlapping character chunks for downstream processing.
"""

from pathlib import Path


def clean_text(text):
    """Strip extra whitespace and drop blank lines."""
    lines = [line.strip() for line in text.splitlines()]
    non_blank = [line for line in lines if line]
    return "\n".join(non_blank)


def chunk_text(text, chunk_size=200, overlap=20):
    """Split text into chunks of chunk_size characters with the given overlap."""
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        piece = text[start:start + chunk_size]
        if piece.strip():
            chunks.append(piece)
        # Stop once we've reached the end of the text.
        if start + chunk_size >= len(text):
            break
    return chunks


def load_and_chunk_documents(data_dir="data", chunk_size=200, overlap=20):
    """Load, clean, and chunk all .txt files in data_dir.

    Returns a list of dicts with keys: source, chunk_index, text.
    """
    all_chunks = []
    data_path = Path(data_dir)

    if not data_path.exists():
        print(f"Error: '{data_dir}' directory not found.")
        return all_chunks

    txt_files = sorted(data_path.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in '{data_dir}'.")
        return all_chunks

    for file_path in txt_files:
        raw = file_path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)

        for chunk_index, piece in enumerate(chunk_text(cleaned, chunk_size, overlap)):
            all_chunks.append({
                "source": file_path.name,
                "chunk_index": chunk_index,
                "text": piece,
            })

    return all_chunks


def main():
    chunks = load_and_chunk_documents()

    print(f"Total chunks loaded: {len(chunks)}")
    print()

    print("Sample chunks (up to 5):")
    print("-" * 60)
    for chunk in chunks[:5]:
        print(f"[{chunk['source']} #{chunk['chunk_index']}]")
        print(chunk["text"])
        print("-" * 60)

    return chunks


if __name__ == "__main__":
    main()
