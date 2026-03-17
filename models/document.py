from dataclasses import dataclass
from sqlite3 import Row


@dataclass
class Document:
    id: int
    tip_inout: str
    data: str
    numar_document: str
    tip_document: str
    emitent_destinatar: str
    descriere: str
    observatii: str
    attachment_path: str
    created_at: str

    @classmethod
    def from_row(cls, row: Row):
        return cls(
            id=row["id"],
            tip_inout=row["tip_inout"],
            data=row["data"],
            numar_document=row["numar_document"],
            tip_document=row["tip_document"],
            emitent_destinatar=row["emitent_destinatar"],
            descriere=row["descriere"] or "",
            observatii=row["observatii"] or "",
            attachment_path=row["attachment_path"] or "",
            created_at=row["created_at"],
        )
