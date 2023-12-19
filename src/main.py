import logging

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_200_OK

from config import settings
from admin.auth.auth_router import router as AdminAuthApiRouter
from admin.dev.dev_router import router as AdminDevApiRouter
from admin.politician.politician_router import router as AdminPoliticianApiRouter
from admin.dashboard.dashboard_router import router as AdminDashboardApiRouter

from public.public_router import router as PublicApiRouter

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.INFO)

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Who-Is-the-Pinocchio API Doc",
        version="0.0.1",
        summary="OpenAPI schema of WIP project",
        # description="",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health-check", status_code=HTTP_200_OK, summary="Health Check")
def health_check_handler() -> str:
    return "For the better world by WIP"


admin_api_version = 1
default_admin_prefix = f"/admin/api/v{admin_api_version}"
app.include_router(
    AdminAuthApiRouter, prefix=f"{default_admin_prefix}/auth", tags=["admin_auth"]
)
app.include_router(
    AdminPoliticianApiRouter,
    prefix=f"{default_admin_prefix}/politician",
    tags=["admin_politician"],
)
app.include_router(
    AdminDashboardApiRouter, prefix=f"{default_admin_prefix}", tags=["admin_dashboard"]
)
# app.include_router(
#     AdminDevApiRouter, prefix=f"{default_admin_prefix}/dev", tags=["admin_dev"]
# )

public_api_version = 1
default_public_prefix = f"/wip/public/api/v{public_api_version}"
app.include_router(
    PublicApiRouter, prefix=f"{default_public_prefix}", tags=["public_web"]
)

initialize_log = f"""

📍 WIP server running successfully.
📍 Swagger URL: {settings.protocol}://{settings.host}:{settings.port}/docs
📍 ReDoc URL: {settings.protocol}://{settings.host}:{settings.port}/redoc
"""

uvicorn_logger.info(initialize_log)
