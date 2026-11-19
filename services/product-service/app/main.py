from shared.metrics import setup_metrics
from shared.logging_config import setup_logging, setup_request_logging
import os
from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, String, Numeric, DateTime, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class ProductRecord(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal


app = FastAPI(title="ShopSphere Product Service", version="2.0.0")

setup_metrics(app, "product-service")
logger = setup_logging("product-service")
setup_request_logging(app, logger)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "service": "product-service",
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductRecord).order_by(ProductRecord.id).all()


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = ProductRecord(
        name=product.name,
        price=product.price
    )

    db.add(new_product)

    try:
        db.commit()
        db.refresh(new_product)
        return new_product
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to create product")
