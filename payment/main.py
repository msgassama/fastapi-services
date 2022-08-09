from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# This should be a different database
redis = get_redis_connection(
        host="redis-15960.c62.us-east-1-4.ec2.cloud.redislabs.com",
        port="15960",
        password="9yA102MrmhaGWn8yH2PWU15ABFOrFphb",
        decode_responses=True
    )

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    qty: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis

@app.get("/orders/{pk}")
def get(pk:str):
    return Order.get(pk)


@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks): # id, qty
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])
    
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total=1.2*product['price'],
        qty=body['qty'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)
    
    return order


def order_completed(order: Order):
    time.sleep(15)
    order.status='completed'
    order.save()
