from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.db.session import Base, engine

# Import all models so they register on Base.metadata before create_all
from api.auth import models as auth_models  # noqa: F401
from api.tenders import models as tender_models  # noqa: F401
from api.documents import models as document_models  # noqa: F401
from api.compliance import models as compliance_models  # noqa: F401
from api.audit import models as audit_models  # noqa: F401

from api.auth.routes import router as auth_router
from api.tenders.routes import router as tenders_router
from api.documents.routes import router as documents_router
from api.compliance.routes import router as compliance_router
from api.audit.routes import router as audit_router
from api.analytics.routes import router as analytics_router
from api.alerts.routes import router as alerts_router
from api.search.routes import router as search_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PramaanAI API",
    description="Evidence-driven procurement verification platform — proof, not just a score.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tenders_router)
app.include_router(documents_router)
app.include_router(compliance_router)
app.include_router(audit_router)
app.include_router(analytics_router)
app.include_router(alerts_router)
app.include_router(search_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
