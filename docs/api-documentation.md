# API
Base path `/api/v1`; interactive docs at `/docs`.
- POST `/auth/register`
- POST `/auth/login`
- GET `/auth/me`
- POST `/documents/upload`
- GET `/documents`
- DELETE `/documents/{doc_id}`
- POST `/analysis/submit`
- GET `/analysis`
- GET `/analysis/{job_id}`
- GET `/analysis/{job_id}/report`
- GET `/admin/dashboard` (ADMIN/SUPER_ADMIN)
Protected endpoints use `Authorization: Bearer <access_token>`.
