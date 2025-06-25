from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

class ProductCreate(BaseModel):
    name: str
    description: str = None
    price: float
    stock: int

class ProductRead(BaseModel):
    id: int
    name: str
    description: str = None
    price: float
    stock: int

    class Config:
        orm_mode = True 