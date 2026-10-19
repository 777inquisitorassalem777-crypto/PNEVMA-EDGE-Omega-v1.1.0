import hashlib, json, sqlite3
from pathlib import Path
from threading import RLock
from .models import utc_now, jsonable

class MemoryStore:
    """Append-only through normal APIs; hash chain detects tampering but is not indestructible."""
    def __init__(self, db_path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        with self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
                payload TEXT NOT NULL, created_at TEXT NOT NULL,
                previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL)""")
            self.db.execute("""CREATE TABLE IF NOT EXISTS proposals(
                proposal_id TEXT PRIMARY KEY, title TEXT NOT NULL, rationale TEXT NOT NULL,
                change_json TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL)""")

    def append(self, event_type, payload):
        with self.lock:
            row = self.db.execute("SELECT event_hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
            prev = row["event_hash"] if row else ""
            created = utc_now()
            payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
            canonical = json.dumps({"event_type": event_type, "payload": json.loads(payload_json),
                "created_at": created, "previous_hash": prev}, ensure_ascii=False, sort_keys=True)
            digest = hashlib.sha256(canonical.encode()).hexdigest()
            with self.db:
                cur = self.db.execute("INSERT INTO events(event_type,payload,created_at,previous_hash,event_hash) VALUES(?,?,?,?,?)",
                    (event_type, payload_json, created, prev, digest))
            return cur.lastrowid

    def record(self, event_type, obj):
        return self.append(event_type, json.loads(jsonable(obj)))

    def events(self, limit=100):
        rows = self.db.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (max(1, limit),)).fetchall()
        return [dict(x) for x in reversed(rows)]

    def verify_chain(self):
        prev = ""
        for row in self.db.execute("SELECT * FROM events ORDER BY id"):
            canonical = json.dumps({"event_type": row["event_type"], "payload": json.loads(row["payload"]),
                "created_at": row["created_at"], "previous_hash": prev}, ensure_ascii=False, sort_keys=True)
            if row["previous_hash"] != prev or hashlib.sha256(canonical.encode()).hexdigest() != row["event_hash"]:
                return False
            prev = row["event_hash"]
        return True

    def save_proposal(self, p):
        now = utc_now()
        with self.db:
            self.db.execute("""INSERT INTO proposals VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(proposal_id) DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at""",
                (p.proposal_id, p.title, p.rationale, json.dumps(p.change, ensure_ascii=False),
                 p.status, now, now))
        self.record("proposal_saved", p)

    def proposals(self):
        result = []
        for row in self.db.execute("SELECT * FROM proposals ORDER BY created_at DESC"):
            item = dict(row); item["change_json"] = json.loads(item["change_json"]); result.append(item)
        return result

    def decide(self, proposal_id, decision, reviewer="local_operator"):
        if decision not in {"accepted", "rejected", "superseded"}: raise ValueError("Invalid decision")
        with self.db:
            cur = self.db.execute("UPDATE proposals SET status=?,updated_at=? WHERE proposal_id=?",
                                  (decision, utc_now(), proposal_id))
            if cur.rowcount != 1: raise KeyError(proposal_id)
        self.append("proposal_decision", {"proposal_id": proposal_id, "decision": decision, "reviewer": reviewer})

    def close(self):
        self.db.close()
