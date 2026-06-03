from fastapi import FastAPI, Path, HTTPException, status
from enum import Enum
from uuid import UUID
from datetime import date

app = FastAPI(title = "E-commerce API")

products_db = {
     1:{"name":"Laptop", "price": 75999, "category": "electronics"},
     2:{"name": "Shirt", "price": 5999, "category": "cloths"},
     3:{"name": "book", "price": 999, "category": "book"}

}

class Category (str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    books = "books"

#1. Simple int converter
@app.get("/products/{product_id}")
def get_product(
    product_id: int = Path(..., gt=0, description = "Product ID must be positive") 
):
    if product_id not in products_db:
        raise HTTPException(status_code = 404, detail = "Product not found")
    return products_db[product_id]
    

# 2. Enum converter
@app.get("/categories/{category}")
def getProductsByCategory (category : Category):
    filtered = [product for product in products_db.values() if product["category"] == category]
    if not filtered:
        raise HTTPException(status_code=404, detail = "no product in this category")
    return{
        "category":category,
        "products": filtered
    }

# 3.Multiple converters
@app.get("/users/{user_id}/reviews/{review_id}")
def get_review(
    user_id: int = Path(..., gt = 0),
    review_id: int = Path(..., gt = 0 , le = 1000)
):
    return{
        "user_id":user_id,
        "review id": review_id,
        "message": f"Review {review_id} by user {user_id}"
    }
# 4. UUID converters for order tracking
orders_db = {}

@app.post("/orders/{order_id}")
def create_order (order_id : UUID):
    orders_db[str(order_id)] = {"status":"pending" , "items": []}

    return{
        "order_id": str(order_id),
        "status": "pending",
        "message": "order created"
    }

@app.get("/orders/{order_id}")
def create_order(order_id: UUID):
    if str(order_id) not in orders_db:
        raise HTTPException(404,"order not found")
    return orders_db[str(order_id)]

# Date converter for reports
@app.get("/sports/{year}/{month}/{day}")
def get_daily_report(
    year: int = Path(...,gt = 2000, le = 2026),
    month: int = Path(..., ge = 1, le = 12),
    day: int = Path(..., ge = 1, le = 31)
):
    report_date = date(year,month,day)
    return{
        "date": report_date.isoformat(),
        "sales": 1000,
        "message": f"report for {report_date}"
    }


