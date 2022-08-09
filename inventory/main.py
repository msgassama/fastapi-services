from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

redis = get_redis_connection(
        host="redis-15960.c62.us-east-1-4.ec2.cloud.redislabs.com",
        port="15960",
        password="9yA102MrmhaGWn8yH2PWU15ABFOrFphb",
        decode_responses=True
    )

class Product(HashModel):
    name: str
    price: float
    qty: int

    class Meta:
        database = redis


@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)

    return {
        'id':product.pk,
        'name':product.name,
        'price':product.price,
        'qty':product.qty
    }

@app.post("/products")
def create(product: Product):
    return product.save()

@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete(pk: str):
   return Product.delete(pk)