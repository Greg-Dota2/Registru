import sqlite3
from pathlib import Path
from typing import Optional, List, Dict
from models.document import Document


class DatabaseManager:
    def __init__(self, db_path: str = "registru.db"):
        self.db_path = str(Path(db_path).resolve())
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tip_inout TEXT NOT NULL,
                data TEXT NOT NULL,
                numar_document TEXT NOT NULL,
                tip_document TEXT NOT NULL,
                emitent_destinatar TEXT NOT NULL,
                descriere TEXT,
                observatii TEXT,
                attachment_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_document(
        self,
        tip_inout: str,
        data: str,
        numar_document: str,
        tip_document: str,
        emitent_destinatar: str,
        descriere: str,
        observatii: str,
        attachment_path: Optional[str],
    ) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (tip_inout, data, numar_document, tip_document, emitent_destinatar, descriere, observatii, attachment_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tip_inout,
                data,
                numar_document,
                tip_document,
                emitent_destinatar,
                descriere,
                observatii,
                attachment_path,
                data,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_document(
        self,
        doc_id: int,
        tip_inout: str,
        data: str,
        numar_document: str,
        tip_document: str,
        emitent_destinatar: str,
        descriere: str,
        observatii: str,
        attachment_path: Optional[str],
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE documents SET
                tip_inout=?,
                data=?,
                numar_document=?,
                tip_document=?,
                emitent_destinatar=?,
                descriere=?,
                observatii=?,
                attachment_path=?
            WHERE id=?
            """,
            (
                tip_inout,
                data,
                numar_document,
                tip_document,
                emitent_destinatar,
                descriere,
                observatii,
                attachment_path,
                doc_id,
            ),
        )
        self.conn.commit()

    def delete_document(self, doc_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id=?", (doc_id,))
        self.conn.commit()

    def get_document_by_id(self, doc_id: int) -> Optional[Document]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id=?", (doc_id,))
        row = cursor.fetchone()
        if row:
            return Document.from_row(row)
        return None

    def get_documents(
        self,
        tip_inout: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM documents WHERE 1=1"
        params = []

        if tip_inout:
            query += " AND tip_inout = ?"
            params.append(tip_inout)

        if date_from:
            query += " AND data >= ?"
            params.append(date_from)

        if date_to:
            query += " AND data <= ?"
            params.append(date_to)

        if search:
            q = f"%{search}%"
            query += " AND (numar_document LIKE ? OR emitent_destinatar LIKE ? OR descriere LIKE ? OR observatii LIKE ? OR tip_document LIKE ?)"
            params.extend([q, q, q, q, q])

        query += " ORDER BY data DESC, id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def get_recent_documents(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(1) AS total FROM documents")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(1) AS intrari FROM documents WHERE tip_inout='Intrare'")
        intrari = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(1) AS iesiri FROM documents WHERE tip_inout='Ieșire'")
        iesiri = cursor.fetchone()[0]
        return {"total": total, "intrari": intrari, "iesiri": iesiri}
