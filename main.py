from fastapi import FastAPI

from app.domains.ceo_test.adapter.inbound.api.ceo_test_router import (
    router as ceo_test_router,
)
from app.domains.dashboard_access.adapter.inbound.api.dashboard_auth_router import (
    create_dashboard_auth_router,
)
from app.domains.dashboard_access.adapter.inbound.api.gate_token_dependency import (
    make_require_gate_token,
)
from app.domains.dashboard_access.application.usecase.issue_gate_token_usecase import (
    IssueGateTokenUseCase,
)
from app.domains.dashboard_access.application.usecase.verify_dashboard_password_usecase import (
    VerifyDashboardPasswordUseCase,
)
from app.domains.dashboard_access.application.usecase.verify_gate_session_usecase import (
    VerifyGateSessionUseCase,
)
from app.domains.tracking.analytics.adapter.inbound.api.analytics_router import (
    create_analytics_router,
)
from app.domains.tracking.ingestion.adapter.inbound.api.tracking_event_router import (
    create_tracking_event_router,
)
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.bootstrap import bootstrap_database
from app.infrastructure.database.engine import (
    create_database_engine,
    create_session_factory,
)
from app.infrastructure.database.session import make_session_dependency
from app.infrastructure.middleware.cors import register_cors_middleware

settings: Settings = get_settings()

engine = create_database_engine(settings)
session_factory = create_session_factory(engine)
get_db_session = make_session_dependency(session_factory)

bootstrap_database(engine)

verify_dashboard_password_usecase = VerifyDashboardPasswordUseCase(
    settings.dashboard_password
)
issue_gate_token_usecase = IssueGateTokenUseCase(
    settings.dashboard_token_secret,
    settings.dashboard_token_ttl_seconds,
)
verify_gate_session_usecase = VerifyGateSessionUseCase(
    settings.dashboard_token_secret
)
require_gate_token = make_require_gate_token(
    verify_gate_session_usecase,
    settings.dashboard_cookie_name,
)

app = FastAPI(debug=settings.debug)
register_cors_middleware(app, settings)
app.include_router(ceo_test_router)
app.include_router(create_tracking_event_router(get_db_session))
app.include_router(
    create_dashboard_auth_router(
        verify_password_usecase=verify_dashboard_password_usecase,
        issue_gate_token_usecase=issue_gate_token_usecase,
        verify_gate_session_usecase=verify_gate_session_usecase,
        cookie_name=settings.dashboard_cookie_name,
        cookie_secure=settings.dashboard_cookie_secure,
    )
)
app.include_router(
    create_analytics_router(
        session_dependency=get_db_session,
        require_gate_token=require_gate_token,
    )
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=33333)
