
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import secrets

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    BackgroundTasks,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db, SessionLocal
from app.models import User, Role, Document, AnalysisJob
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut, AnalysisIn
from app.security import (
    hash_password,
    verify_password,
    make_token,
    current_user,
    roles,
)
from app.core.config import settings

from app.services.extraction import (
    ALLOWED,
    extract,
    language,
    validate_upload,
)

from app.services.analysis import run


router = APIRouter(prefix="/api/v1")


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

@router.post("/auth/register", response_model=TokenOut)
async def register(
    data: RegisterIn,
    db: AsyncSession = Depends(get_db),
):
    email = data.email.lower().strip()

    existing_user = await db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    role = Role.STUDENT

    if (
        settings.bootstrap_admin_email
        and email == settings.bootstrap_admin_email.lower().strip()
        and settings.bootstrap_admin_password
        and data.password == settings.bootstrap_admin_password
    ):
        role = Role.ADMIN

    user = User(
        full_name=data.full_name,
        email=email,
        password_hash=hash_password(data.password),
        role=role,
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Registration could not be completed",
        )

    return TokenOut(
        access_token=make_token(user.id),
        user=user,
    )


@router.post("/auth/login", response_model=TokenOut)
async def login(
    data: LoginIn,
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(
        select(User).where(
            User.email == data.email.lower().strip()
        )
    )

    if (
        not user
        or not verify_password(data.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    return TokenOut(
        access_token=make_token(user.id),
        user=user,
    )


@router.get("/auth/me", response_model=UserOut)
async def me(
    user: User = Depends(current_user),
):
    return user


# --------------------------------------------------
# SECURE DOCUMENT UPLOAD
# --------------------------------------------------

@router.post("/documents/upload")
async def upload(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    path = None

    try:
        # 1. Validate filename
        original_name = (file.filename or "").strip()

        if not original_name:
            raise HTTPException(
                status_code=400,
                detail="Filename is required",
            )

        # Handle both Windows and Unix path separators
        safe_name = PureWindowsPath(
            original_name.replace("/", "\\")
        ).name

        safe_name = Path(safe_name).name

        if (
            not safe_name
            or safe_name in {".", ".."}
            or len(safe_name) > 255
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename",
            )

        extension = Path(safe_name).suffix.lower()

        # 2. Validate extension
        if extension not in ALLOWED:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type",
            )

        # 3. Read only configured maximum size + 1 byte
        max_bytes = settings.max_upload_mb * 1024 * 1024

        data = await file.read(max_bytes + 1)

        if len(data) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail="File exceeds configured size limit",
            )

        if not data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        # 4. Validate actual file content
        try:
            validate_upload(data, extension)

        except ValueError as exc:
            raise HTTPException(
                status_code=415,
                detail=str(exc),
            )

        # 5. Extract text before permanent storage
        temp_folder = Path(settings.upload_dir).resolve()
        temp_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = temp_folder / (
            secrets.token_hex(16) + extension
        )

        path.write_bytes(data)

        try:
            extracted_text = extract(str(path))

        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Text extraction failed: {type(exc).__name__}",
            )

        # 6. Reject documents without extractable text
        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text found. "
                    "The document may be scanned or image-only."
                ),
            )

        # 7. Detect language
        detected_language = language(extracted_text)

        # 8. Save document metadata
        document = Document(
            owner_id=user.id,
            filename=safe_name,
            file_type=extension[1:],
            file_size=len(data),
            storage_path=str(path),
            extracted_text=extracted_text,
            detected_language=detected_language,
        )

        db.add(document)

        try:
            await db.commit()
            await db.refresh(document)

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Document could not be saved",
            )

        return {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "characters_extracted": len(extracted_text),
            "detected_language": document.detected_language,
            "status": "uploaded",
        }

    except HTTPException:
        if path is not None:
            path.unlink(missing_ok=True)
        raise

    except Exception as exc:
        if path is not None:
            path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {type(exc).__name__}",
        )

    finally:
        await file.close()


# --------------------------------------------------
# DOCUMENT LIST
# --------------------------------------------------

@router.get("/documents")
async def documents(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.scalars(
            select(Document)
            .where(Document.owner_id == user.id)
            .order_by(desc(Document.created_at))
        )
    ).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "detected_language": document.detected_language,
        }
        for document in rows
    ]


# --------------------------------------------------
# DOCUMENT DELETE
# --------------------------------------------------

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await db.scalar(
        select(Document).where(
            Document.id == doc_id,
            Document.owner_id == user.id,
        )
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    storage_path = Path(document.storage_path)

    await db.delete(document)

    try:
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Document could not be deleted",
        )

    # Remove physical file after successful database deletion
    try:
        storage_path.unlink(missing_ok=True)
    except OSError:
        pass

    return {
        "deleted": True,
        "document_id": doc_id,
    }


# --------------------------------------------------
# BACKGROUND ANALYSIS PROCESSING
# --------------------------------------------------

async def process_job(job_id: int):
    async with SessionLocal() as db:

        job = await db.get(AnalysisJob, job_id)

        if not job:
            return

        job.status = "PROCESSING"
        await db.commit()

        try:
            doc = await db.get(
                Document,
                job.document_id,
            )

            if not doc:
                raise ValueError("Analysis document not found")

            corpus = (
                await db.scalars(
                    select(Document).where(
                        Document.owner_id == job.user_id,
                        Document.id != doc.id,
                    )
                )
            ).all()

            job.result_json = run(
                doc.extracted_text,
                doc.filename,
                job.analysis_type,
                [
                    {
                        "filename": item.filename,
                        "text": item.extracted_text,
                    }
                    for item in corpus
                ],
            )

            job.status = "COMPLETED"
            job.progress = 100
            job.error_message = None

        except Exception as exc:
            await db.rollback()

            job = await db.get(
                AnalysisJob,
                job_id,
            )

            if not job:
                return

            job.status = "FAILED"
            job.error_message = type(exc).__name__

        job.completed_at = datetime.now(timezone.utc)

        await db.commit()


# --------------------------------------------------
# SUBMIT ANALYSIS
# --------------------------------------------------

@router.post("/analysis/submit")
async def submit(
    data: AnalysisIn,
    bg: BackgroundTasks,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await db.scalar(
        select(Document).where(
            Document.id == data.document_id,
            Document.owner_id == user.id,
        )
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    job = AnalysisJob(
        user_id=user.id,
        document_id=doc.id,
        analysis_type=data.analysis_type,
        status="QUEUED",
        progress=0,
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    bg.add_task(process_job, job.id)

    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
    }


# --------------------------------------------------
# ANALYSIS HISTORY
# --------------------------------------------------

@router.get("/analysis")
async def analyses(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.scalars(
            select(AnalysisJob)
            .where(AnalysisJob.user_id == user.id)
            .order_by(desc(AnalysisJob.created_at))
        )
    ).all()

    return [
        {
            "id": job.id,
            "document_id": job.document_id,
            "analysis_type": job.analysis_type,
            "status": job.status,
            "progress": job.progress,
        }
        for job in rows
    ]


# --------------------------------------------------
# SINGLE ANALYSIS RESULT
# --------------------------------------------------

@router.get("/analysis/{job_id}")
async def analysis(
    job_id: int,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await db.scalar(
        select(AnalysisJob).where(
            AnalysisJob.id == job_id,
            AnalysisJob.user_id == user.id,
        )
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "error": job.error_message,
        "result": job.result_json,
    }


# --------------------------------------------------
# ANALYSIS REPORT
# --------------------------------------------------

@router.get("/analysis/{job_id}/report")
async def report(
    job_id: int,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await db.scalar(
        select(AnalysisJob).where(
            AnalysisJob.id == job_id,
            AnalysisJob.user_id == user.id,
        )
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    if job.status != "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail="Analysis is not complete",
        )

    return {
        "analysis_id": job.id,
        "generated_at": job.completed_at,
        "result": job.result_json,
        "notice": "Evidence is not a misconduct verdict.",
    }


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@router.get("/admin/dashboard")
async def admin(
    user: User = Depends(
        roles(Role.ADMIN, Role.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
):
    users = (
        await db.scalars(select(User))
    ).all()

    docs = (
        await db.scalars(select(Document))
    ).all()

    jobs = (
        await db.scalars(select(AnalysisJob))
    ).all()

    return {
        "users": len(users),
        "documents": len(docs),
        "analyses": len(jobs),
        "pending_jobs": sum(
            job.status in {"QUEUED", "PROCESSING"}
            for job in jobs
        ),
        "failed_jobs": sum(
            job.status == "FAILED"
            for job in jobs
        ),
    }
