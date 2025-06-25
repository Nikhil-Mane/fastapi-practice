from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.cart import CartItem, CartItemCreate, CartItemRead
from ..models.product import Product
from ..services.db import get_db
from ..services.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])

@router.post("/add", response_model=CartItemRead)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    cart_item = db.query(CartItem).filter(CartItem.user_id == user.id, CartItem.product_id == item.product_id).first()
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(user_id=user.id, product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.get("/", response_model=list[CartItemRead])
def view_cart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(CartItem).filter(CartItem.user_id == user.id).all()

@router.post("/remove", response_model=dict)
def remove_from_cart(item: CartItemCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart_item = db.query(CartItem).filter(CartItem.user_id == user.id, CartItem.product_id == item.product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(cart_item)
    db.commit()
    return {"detail": "Item removed from cart"}

@router.post("/clear", response_model=dict)
def clear_cart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    return {"detail": "Cart cleared"} 