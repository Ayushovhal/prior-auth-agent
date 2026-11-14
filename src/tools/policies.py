"""Policy retrieval.

Policies are markdown with stable section ids. Chunks are one section each so
a citation can point at ``POL-KNEE-MRI-1.1`` rather than a random paragraph.
Embeddings are sentence-transformers ``all-MiniLM-L6-v2``, stored in Chroma.
An unknown procedure or a blank query returns no chunks.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from tools.catalog import parse_front_matter, policies_dir, resolve_procedure
from tools.patients import project_root

SECTION_ID = re.compile(r"\(([A-Z]+(?:-[A-Z0-9]+)+-\d+\.\d+)\)")
_MODEL = "all-MiniLM-L6-v2"


def _chunks() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    for path in sorted(policies_dir().glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        procedure = str(meta.get("procedure", ""))
        policy_id = str(meta.get("policy_id", path.stem))
        for part in re.split(r"(?m)^### ", body)[1:]:
            heading, _, text = part.partition("\n")
            match = SECTION_ID.search(heading)
            if not match:
                continue
            chunks.append(
                {
                    "id": match.group(1),
                    "section_id": match.group(1),
                    "policy_id": policy_id,
                    "procedure": procedure,
                    "heading": heading.strip(),
                    "text": text.strip(),
                }
            )
    return chunks


@lru_cache(maxsize=4)
def _collection(index_dir: str) -> Any:
    path = Path(index_dir)
    path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(path))
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_MODEL
    )
    collection = client.get_or_create_collection(
        name="policies",
        embedding_function=embedder,
        metadata={"hnsw:space": "cosine"},
    )
    chunks = _chunks()
    stored = set(collection.get(include=[])["ids"])
    missing = [chunk for chunk in chunks if chunk["id"] not in stored]
    if missing:
        collection.add(
            ids=[chunk["id"] for chunk in missing],
            documents=[f"{chunk['heading']}\n{chunk['text']}" for chunk in missing],
            metadatas=[
                {
                    "section_id": chunk["section_id"],
                    "policy_id": chunk["policy_id"],
                    "procedure": chunk["procedure"],
                    "heading": chunk["heading"],
                }
                for chunk in missing
            ],
        )
    return collection


def search_policy(
    procedure: str,
    query: str,
    k: int = 4,
    index_dir: str | None = None,
) -> list[dict[str, Any]]:
    """Return the top policy sections for one procedure.

    Unknown procedures and blank queries return an empty list.
    """
    canonical = resolve_procedure(procedure)
    cleaned = query.strip()
    if canonical is None or not cleaned:
        return []
    directory = index_dir or str(project_root() / ".chroma")
    collection = _collection(directory)
    result = collection.query(
        query_texts=[cleaned],
        n_results=k,
        where={"procedure": canonical},
        include=["documents", "metadatas", "distances"],
    )
    hits: list[dict[str, Any]] = []
    ids = result["ids"][0]
    for index, section_id in enumerate(ids):
        meta = result["metadatas"][0][index]
        hits.append(
            {
                "section_id": section_id,
                "policy_id": meta["policy_id"],
                "procedure": meta["procedure"],
                "heading": meta["heading"],
                "text": result["documents"][0][index],
                "distance": result["distances"][0][index],
            }
        )
    return hits
