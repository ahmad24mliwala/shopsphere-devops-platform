from shared.metrics import setup_metrics

import os

from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    create_engine,
    BigInteger,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    func,
    text
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    Session
)

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class OrderReference(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class PaymentRecord(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id"),
        unique=True,
        nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    method: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        server_default="SIMULATED_SUCCESS"
    )

    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    method: str = Field(default="SIMULATED", min_length=1, max_length=50)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    method: str
    status: str


app = FastAPI(
    title="ShopSphere Payment Service",
    version="2.0.0"
)

setup_metrics(app, "payment-service")


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
            "service": "payment-service",
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/payments", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    return db.query(PaymentRecord).order_by(PaymentRecord.id).all()


@app.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=201
)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    new_payment = PaymentRecord(
        order_id=payment.order_id,
        amount=payment.amount,
        method=payment.method,
        status="SIMULATED_SUCCESS"
    )

    db.add(new_payment)

    try:
        db.commit()
        db.refresh(new_payment)
        return new_payment

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Order does not exist or a payment already exists for this order"
        )
