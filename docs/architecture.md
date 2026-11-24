# Architecture
Next.js is the presentation layer. FastAPI owns authentication, validation, private document storage and analysis orchestration. SQLAlchemy persists users, documents and jobs. SQLite is the easy local default; PostgreSQL/pgvector is the production target. Redis is provisioned for background workers.

Upload -> validate -> private store -> extract -> job -> orchestrator -> semantic or code engine -> persist JSON -> owner-only report.

Five agents: Analysis Orchestrator, Document Intelligence, Multilingual Analysis, Code Analysis, Report Generation. Agents have no unrestricted shell or network tools.
