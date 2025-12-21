from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
import re


class OrderItem(BaseModel):
    menu_item_id: int = Field(..., gt=0, description="ID позиции в меню")
    name: str = Field(..., min_length=2, max_length=100)
    quantity: int = Field(..., gt=0, le=20, description="Количество от 1 до 20")
    price: float = Field(..., gt=0, description="Цена за единицу")
    modifiers: List[str] = Field(default_factory=list)


class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_phone: str = Field(..., min_length=5, max_length=20)
    items: List[OrderItem]
    delivery_address: Optional[str] = None
    is_delivery: bool = False
    special_instructions: Optional[str] = None
    
    @validator('customer_phone')
    def validate_phone(cls, v):
        # Простая валидация телефона
        phone_pattern = r'^[\d\s\-\+\(\)]{5,20}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Некорректный формат телефона')
        return v
    
    @validator('delivery_address')
    def validate_delivery_address(cls, v, values):
        if values.get('is_delivery') and not v:
            raise ValueError('Адрес доставки обязателен при выборе доставки')
        return v
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Заказ должен содержать хотя бы одну позицию')
        return v


class OrderResponse(BaseModel):
    order_id: str
    status: str  # "created", "processing", "ready", "delivered", "cancelled"
    total_amount: float
    discount_amount: float
    final_amount: float
    estimated_minutes: int
    created_at: datetime
    customer_name: str
    customer_phone: str
    items: List[OrderItem]
    is_delivery: bool
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None


class MenuItem(BaseModel):
    id: int
    name: str
    category: str  # "pizza", "salad", "drink", "dessert"
    description: Optional[str]
    price: float
    available: bool = True
    preparation_minutes: int


class MenuResponse(BaseModel):
    categories: List[str]
    items: List[MenuItem]


class StatusRequest(BaseModel):
    order_id: str


class CancelRequest(BaseModel):
    order_id: str
    reason: Optional[str] = None
