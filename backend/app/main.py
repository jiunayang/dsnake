from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import Base, engine
from app.core.limiter import limiter
from app.routers.snakes import router as snakes_router
from app.models.snake import Snake
from app.models.admin import Admin
from app.core.security import get_password_hash

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(snakes_router, prefix=settings.API_V1_STR, tags=["snakes"])


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not existing_admin:
            admin = Admin(
                username="admin",
                password_hash=get_password_hash("admin123")
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Snake Encyclopedia API", "version": settings.VERSION}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
