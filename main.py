import logging

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/", status_code=200, summary="Health Check")
def health_check_handler():
    return "For the better world by WIP"


initialize_log = f"""

📍 WIP server running successfully.
📍 Swagger URL: http://localhost:{8000}/docs
📍 ReDoc URL: http://localhost:{8000}/redoc
"""

uvicorn_logger.info(initialize_log)
