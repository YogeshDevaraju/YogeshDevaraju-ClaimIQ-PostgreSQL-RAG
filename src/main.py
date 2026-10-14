from src.api.routes.rag_chat import router as rag_chat_router
from fastapi import FastAPI

from src.api.routes import (
    ai,
    analytics,
    audit_logs,
    claims,
    documents,
    health,
    policies,
    users,
)


app = FastAPI(
    title="ClaimIQ",
    version="1.0.0",
)


app.include_router(
    health.router,
    prefix="/api/v1",
)

app.include_router(
    users.router,
    prefix="/api/v1",
)

app.include_router(
    policies.router,
    prefix="/api/v1",
)

app.include_router(
    claims.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    ai.router,
    prefix="/api/v1",
)

app.include_router(
    analytics.router,
    prefix="/api/v1",
)

app.include_router(
    audit_logs.router,
    prefix="/api/v1",
)

app.include_router(rag_chat_router)

