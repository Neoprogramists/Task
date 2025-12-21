from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import logging
from models import OrderRequest, OrderResponse, MenuItem, MenuResponse


class OrderService:
    def __init__(self):
        self.orders: Dict[str, OrderResponse] = {}
        self.delivery_fee: float = 200.00
        self.discount_threshold: float = 1000.00
        self.discount_percent: float = 10
        self.logger = logging.getLogger(__name__)
        
        # Пример меню
        self.menu_items = [
            MenuItem(
                id=101,
                name="Пицца Маргарита",
                category="pizza",
                description="Томаты, моцарелла, базилик",
                price=650.00,
                preparation_minutes=25
            ),
            MenuItem(
                id=102,
                name="Пицца Пепперони",
                category="pizza",
                description="Пепперони, моцарелла, томатный соус",
                price=750.00,
                preparation_minutes=25
            ),
            MenuItem(
                id=201,
                name="Салат Цезарь",
                category="salad",
                description="Курица, салат, гренки, соус Цезарь",
                price=350.00,
                preparation_minutes=15
            ),
            MenuItem(
                id=301,
                name="Кола",
                category="drink",
                description="0.5л",
                price=150.00,
                preparation_minutes=5
            ),
            MenuItem(
                id=302,
                name="Кофе Латте",
                category="drink",
                description="350мл",
                price=250.00,
                preparation_minutes=10
            ),
            MenuItem(
                id=401,
                name="Тирамису",
                category="dessert",
                description="Классический итальянский десерт",
                price=300.00,
                preparation_minutes=5
            )
        ]
    
    def create_order(self, request: OrderRequest) -> OrderResponse:
        """Создание нового заказа"""
        try:
            # 1. Валидация наличия блюд в меню
            self._validate_menu_items(request.items)
            
            # 2. Расчет стоимости
            items_total = self._calculate_items_total(request.items)
            delivery_fee = self.delivery_fee if request.is_delivery else 0
            subtotal = items_total + delivery_fee
            
            # 3. Применение скидки
            discount = self._calculate_discount(subtotal)
            final_amount = subtotal - discount
            
            # 4. Расчет времени приготовления
            estimated_minutes = self._calculate_estimated_time(request)
            
            # 5. Генерация ID заказа
            order_id = self._generate_order_id()
            
            # 6. Создание ответа
            response = OrderResponse(
                order_id=order_id,
                status="created",
                total_amount=round(subtotal, 2),
                discount_amount=round(discount, 2),
                final_amount=round(final_amount, 2),
                estimated_minutes=estimated_minutes,
                created_at=datetime.utcnow(),
                customer_name=request.customer_name,
                customer_phone=request.customer_phone,
                items=request.items,
                is_delivery=request.is_delivery,
                delivery_address=request.delivery_address,
                special_instructions=request.special_instructions
            )
            
            # 7. Сохранение заказа
            self.orders[order_id] = response
            
            self.logger.info(f"Заказ создан: {order_id} для {request.customer_name}")
            
            # Симуляция изменения статуса через время
            self._schedule_status_updates(order_id, estimated_minutes)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Ошибка создания заказа: {str(e)}")
            raise
    
    def _validate_menu_items(self, items: List[OrderItem]) -> None:
        """Проверка что все позиции есть в меню"""
        menu_item_ids = {item.id for item in self.menu_items}
        for order_item in items:
            if order_item.menu_item_id not in menu_item_ids:
                raise ValueError(f"Позиция с ID {order_item.menu_item_id} отсутствует в меню")
    
    def _calculate_items_total(self, items: List[OrderItem]) -> float:
        """Расчет общей стоимости позиций"""
        return sum(item.price * item.quantity for item in items)
    
    def _calculate_discount(self, subtotal: float) -> float:
        """Расчет скидки"""
        if subtotal >= self.discount_threshold:
            return subtotal * (self.discount_percent / 100)
        return 0
    
    def _calculate_estimated_time(self, request: OrderRequest) -> int:
        """Расчет времени выполнения заказа"""
        # Базовая подготовка
        base_time = 15
        
        # Время приготовления позиций
        items_time = 0
        for order_item in request.items:
            menu_item = next((m for m in self.menu_items if m.id == order_item.menu_item_id), None)
            if menu_item:
                items_time = max(items_time, menu_item.preparation_minutes)
        
        # Время на дополнительные позиции
        extra_items_time = max(0, len(request.items) - 1) * 5
        
        # Время доставки
        delivery_time = 25 if request.is_delivery else 0
        
        return base_time + items_time + extra_items_time + delivery_time
    
    def _generate_order_id(self) -> str:
        """Генерация уникального ID заказа"""
        date_str = datetime.now().strftime("%Y%m%d")
        unique_str = str(uuid.uuid4())[:8].upper()
        return f"ORD-{date_str}-{unique_str}"
    
    def _schedule_status_updates(self, order_id: str, total_minutes: int) -> None:
        """Симуляция обновления статуса заказа (в реальности через очередь)"""
        # В реальном приложении здесь была бы интеграция с Celery/RQ
        pass
    
    def get_order_status(self, order_id: str) -> Optional[OrderResponse]:
        """Получение статуса заказа"""
        return self.orders.get(order_id)
    
    def cancel_order(self, order_id: str, reason: Optional[str] = None) -> bool:
        """Отмена заказа"""
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in ["created", "processing"]:
                order.status = "cancelled"
                self.logger.info(f"Заказ отменен: {order_id}, причина: {reason}")
                return True
        return False
    
    def get_menu(self, category: Optional[str] = None) -> MenuResponse:
        """Получение меню"""
        items = self.menu_items
        
        if category:
            items = [item for item in items if item.category == category]
        
        # Только доступные позиции
        available_items = [item for item in items if item.available]
        
        # Уникальные категории
        categories = list(set(item.category for item in available_items))
        
        return MenuResponse(
            categories=categories,
            items=available_items
        )
    
    def get_order_history(self, customer_phone: str) -> List[OrderResponse]:
        """Получение истории заказов по телефону"""
        return [
            order for order in self.orders.values()
            if order.customer_phone == customer_phone
        ]


class PaymentService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_payment(self, order_id: str, amount: float, 
                       payment_method: str = "card") -> Dict:
        """Обработка платежа"""
        try:
            # Симуляция платежного шлюза
            payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # В реальности здесь была бы интеграция с платежной системой
            is_success = amount > 0  # Всегда успешно для демо
            
            if is_success:
                return {
                    "payment_id": payment_id,
                    "status": "success",
                    "amount": amount,
                    "payment_method": payment_method,
                    "transaction_time": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "payment_id": payment_id,
                    "status": "failed",
                    "error": "Payment processing failed",
                    "transaction_time": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Ошибка обработки платежа: {str(e)}")
            raise
