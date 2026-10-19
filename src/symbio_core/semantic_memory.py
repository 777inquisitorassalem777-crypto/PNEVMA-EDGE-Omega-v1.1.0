
"""Optional PostgreSQL + pgvector semantic memory. Requires psycopg and pgvector packages."""
from __future__ import annotations
import json
import os
from typing import Sequence

class SemanticMemoryError(RuntimeError): pass

class PostgresSemanticMemory:
    def __init__(self, dsn=None, dimensions=384):
        self.dsn = dsn or os.getenv("SYMBIO_POSTGRES_DSN", "postgresql://symbio:symbio@localhost:5432/symbio")
        self.dimensions = int(dimensions)
        if self.dimensions <= 0: raise ValueError("dimensions must be positive")
        try:
            import psycopg
            from pgvector.psycopg import register_vector
        except ImportError as exc:
            raise SemanticMemoryError("Install optional dependencies: pip install '.[postgres]'") from exc
        self.conn = psycopg.connect(self.dsn)
        self.conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        self.conn.execute(f"""CREATE TABLE IF NOT EXISTS semantic_memories (
            id BIGSERIAL PRIMARY KEY, content TEXT NOT NULL, metadata JSONB NOT NULL DEFAULT '{{}}',
            embedding vector({self.dimensions}) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
        self.conn.commit()
        register_vector(self.conn)

    def add(self, content: str, embedding: Sequence[float], metadata=None):
        if not content.strip(): raise ValueError("content must not be empty")
        if len(embedding) != self.dimensions: raise ValueError(f"embedding must have {self.dimensions} dimensions")
        self.conn.execute("INSERT INTO semantic_memories(content, metadata, embedding) VALUES (%s,%s,%s)",
                          (content, json.dumps(metadata or {}), list(map(float, embedding))))
        self.conn.commit()

    def search(self, embedding: Sequence[float], limit=5):
        if len(embedding) != self.dimensions: raise ValueError(f"embedding must have {self.dimensions} dimensions")
        rows = self.conn.execute("""SELECT id, content, metadata, 1 - (embedding <=> %s) AS similarity, created_at
            FROM semantic_memories ORDER BY embedding <=> %s LIMIT %s""",
            (list(map(float, embedding)), list(map(float, embedding)), max(1, min(int(limit),100)))).fetchall()
        return [{"id":r[0],"content":r[1],"metadata":r[2],"similarity":float(r[3]),"created_at":r[4].isoformat()} for r in rows]

    def close(self): self.conn.close()
