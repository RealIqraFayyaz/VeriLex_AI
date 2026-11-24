
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, BadZipFile

from pypdf import PdfReader
from docx import Document as Docx


ALLOWED = {
    ".pdf", ".docx", ".txt",
    ".py", ".java", ".js", ".jsx",
    ".ts", ".tsx", ".c", ".cpp",
    ".h", ".hpp", ".php",
}

TEXT_EXTENSIONS = ALLOWED - {".pdf", ".docx"}


def validate_upload(data: bytes, extension: str) -> None:
    """Validate file contents against the declared extension."""

    if not data:
        raise ValueError("Uploaded file is empty")

    ext = extension.lower()

    if ext not in ALLOWED:
        raise ValueError("Unsupported file extension")

    if ext == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file")

    elif ext == ".docx":
        try:
            with ZipFile(BytesIO(data)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise ValueError("Invalid DOCX document")
        except BadZipFile:
            raise ValueError("Invalid DOCX file")

    else:
        if b"\x00" in data:
            raise ValueError("Binary files are not supported")


def extract(path: str) -> str:
    """Extract text from supported document formats."""

    file_path = Path(path)
    extension = file_path.suffix.lower()

    if extension not in ALLOWED:
        raise ValueError("Unsupported file extension")

    if not file_path.is_file():
        raise FileNotFoundError("Document does not exist")

    if extension == ".pdf":
        reader = PdfReader(str(file_path), strict=False)

        if reader.is_encrypted:
            raise ValueError("Encrypted PDF is not supported")

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages).strip()

    if extension == ".docx":
        document = Docx(str(file_path))
        paragraphs = [p.text for p in document.paragraphs]

        for table in document.tables:
            for row in table.rows:
                paragraphs.append(
                    " | ".join(cell.text for cell in row.cells)
                )

        return "\n".join(paragraphs).strip()

    return file_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    ).strip()


def language(text: str) -> str:
    """Detect language when enough text is available."""

    if not isinstance(text, str) or len(text.strip()) < 20:
        return "unknown"

    try:
        from langdetect import detect, DetectorFactory

        DetectorFactory.seed = 0
        return detect(text[:5000])

    except Exception:
        return "unknown"


def chunks(text: str, size: int = 900, overlap: int = 120):
    """Split text into overlapping chunks."""

    if size <= 0:
        raise ValueError("Chunk size must be positive")

    if overlap < 0 or overlap >= size:
        raise ValueError("Overlap must be smaller than chunk size")

    text = " ".join(text.split())

    if not text:
        return []

    result = []
    start = 0

    while start < len(text):
        end = min(len(text), start + size)
        result.append(text[start:end])

        if end >= len(text):
            break

        start = end - overlap

    return result
