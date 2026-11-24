# Deployment
Deploy `frontend/` to Vercel and set `NEXT_PUBLIC_API_URL=https://your-api-host/api/v1`.

Do not deploy the whole stack to Vercel. Host FastAPI and its worker as containers on a container-capable service. Use managed PostgreSQL with pgvector, managed Redis and private object storage. Configure backend CORS for the exact Vercel domain. Set secrets in provider environment settings. Use HTTPS, backups, logs and data retention policies.
