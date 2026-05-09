from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_admin
from app.core.config import settings
from app.models.admin import Admin
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.snake import SnakeCreate, SnakeUpdate, SnakeListResponse, SnakeListItem, SnakeDetail
from app.models.snake import Snake

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == request.username).first()

    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=timedelta(seconds=access_token_expires)
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=access_token_expires
    )


@limiter.limit("60/minute")
@router.get("/snakes", response_model=SnakeListResponse)
async def get_snakes(
    request: Request,
    search: Optional[str] = Query(None, description="Search by name"),
    is_venomous: Optional[bool] = Query(None, description="Filter by venomous status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = db.query(Snake)

    if search:
        query = query.filter(Snake.name.ilike(f"%{search}%"))

    if is_venomous is not None:
        query = query.filter(Snake.is_venomous == is_venomous)

    total = query.count()
    offset = (page - 1) * page_size
    snakes = query.order_by(Snake.id.desc()).offset(offset).limit(page_size).all()

    return SnakeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[SnakeListItem.model_validate(snake) for snake in snakes]
    )


@router.get("/snakes/{snake_id}", response_model=SnakeDetail)
async def get_snake(snake_id: int, db: Session = Depends(get_db)):
    snake = db.query(Snake).filter(Snake.id == snake_id).first()

    if not snake:
        raise HTTPException(status_code=404, detail="Snake not found")

    return snake


@router.post("/snakes", response_model=SnakeDetail, status_code=status.HTTP_201_CREATED)
async def create_snake(
    snake_data: SnakeCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    snake = Snake(**snake_data.model_dump())
    db.add(snake)
    db.commit()
    db.refresh(snake)

    return snake


@router.put("/snakes/{snake_id}", response_model=SnakeDetail)
async def update_snake(
    snake_id: int,
    snake_data: SnakeUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    snake = db.query(Snake).filter(Snake.id == snake_id).first()

    if not snake:
        raise HTTPException(status_code=404, detail="Snake not found")

    update_data = snake_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(snake, key, value)

    db.commit()
    db.refresh(snake)

    return snake


@router.delete("/snakes/{snake_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snake(
    snake_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    snake = db.query(Snake).filter(Snake.id == snake_id).first()

    if not snake:
        raise HTTPException(status_code=404, detail="Snake not found")

    db.delete(snake)
    db.commit()

    return None
