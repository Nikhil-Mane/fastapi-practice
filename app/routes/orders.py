from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..models.order import Order, OrderCreate, OrderRead
from ..models.product import Product
from ..services.db import get_db
from ..services.auth import get_current_user, require_role
from ..models.cart import CartItem
from ..models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderRead)
def place_order(order: OrderCreate, db: Session = Depends(get_db), request: Request = None, user=Depends(get_current_user)):
    # Check product exists and stock is sufficient
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    # Create order with status 'pending' and set user_id
    db_order = Order(user_id=user.id, product_id=order.product_id, quantity=order.quantity, status='pending')
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    # Enqueue order processing job
    if request is not None:
        job_queue = request.app.state.job_queue
        job_id = f"order_{db_order.id}"
        job_data = {"order_id": db_order.id}
        job_queue.put_nowait((job_id, "order_processing", job_data))
    return db_order

@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/from_cart", response_model=list[OrderRead])
def place_order_from_cart(db: Session = Depends(get_db), request: Request = None, user=Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    orders = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            continue  # Skip items that can't be ordered
        db_order = Order(user_id=user.id, product_id=item.product_id, quantity=item.quantity, status='pending')
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        # Enqueue order processing job
        if request is not None:
            job_queue = request.app.state.job_queue
            job_id = f"order_{db_order.id}"
            job_data = {"order_id": db_order.id}
            job_queue.put_nowait((job_id, "order_processing", job_data))
        orders.append(db_order)
    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    if not orders:
        raise HTTPException(status_code=400, detail="No valid items to order from cart")
    return orders

@router.get("/my", response_model=list[OrderRead])
def get_my_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == user.id).all()

@router.get("/all", response_model=list[OrderRead], dependencies=[Depends(require_role('admin'))])
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@router.get("/user/{user_id}", response_model=list[OrderRead], dependencies=[Depends(require_role('admin'))])
def get_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == user_id).all() 