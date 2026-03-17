import shutil
from pathlib import Path


def backup_database(source_db_path: str, target_db_path: str):
    shutil.copy2(source_db_path, target_db_path)


def copy_attachment(src_path: str, attachments_dir: Path, subfolder: str = "") -> str:
    """Copy a file into attachments/subfolder and return the relative path."""
    dest_dir = attachments_dir / subfolder if subfolder else attachments_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    src = Path(src_path)
    dst = dest_dir / src.name

    # Avoid overwriting a different file with the same name
    counter = 1
    while dst.exists() and dst.read_bytes() != src.read_bytes():
        dst = dest_dir / f"{src.stem}_{counter}{src.suffix}"
        counter += 1

    if not dst.exists():
        shutil.copy2(src_path, dst)

    rel = f"attachments/{subfolder}/{dst.name}" if subfolder else f"attachments/{dst.name}"
    return rel


def resolve_attachment(rel_or_abs_path: str, app_dir: Path) -> Path:
    """Resolve an attachment path to an absolute Path, supporting both old absolute
    paths and new relative 'attachments/...' paths."""
    p = Path(rel_or_abs_path)
    if p.is_absolute():
        return p
    return app_dir / p
