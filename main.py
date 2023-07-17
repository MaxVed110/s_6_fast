# Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары,
# заказы и пользователи.
# Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.
# Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.
import hashlib
import databases
import sqlalchemy
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import List

app = FastAPI()

DATABASE_URL = 'sqlite:///mydatabase.db'

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    'products',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('products_name', sqlalchemy.String(40)),
    sqlalchemy.Column('description', sqlalchemy.String(200)),
    sqlalchemy.Column('cost', sqlalchemy.Integer)
)

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('first_name', sqlalchemy.String(40)),
    sqlalchemy.Column('last_name', sqlalchemy.String(40)),
    sqlalchemy.Column('email', sqlalchemy.String(100)),
    sqlalchemy.Column('password', sqlalchemy.String(100))
)

orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column("produkts_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('data_ord', sqlalchemy.String(30)),
    sqlalchemy.Column('status', sqlalchemy.String(20))
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)


class UserIn(BaseModel):
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=40)
    email: str = Field(max_length=100)
    password: str = Field(max_length=100)


class UserOut(BaseModel):
    id: int
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=40)
    email: str = Field(max_length=100)


class ProductIn(BaseModel):
    products_name: str = Field(max_length=40)
    description: str = Field(max_length=200)
    cost: int


class ProductOut(BaseModel):
    id: int
    products_name: str = Field(max_length=40)
    description: str = Field(max_length=200)
    cost: int


class OrderIn(BaseModel):
    user_id: int
    produkts_id: int
    data_ord: str = Field(max_length=30)
    status: str = Field(max_length=20)


class OrderOut(BaseModel):
    id: int
    user_id: int
    produkts_id: int
    data_ord: str = Field(max_length=30)
    status: str = Field(max_length=20)


@app.get('/users', response_model=List[UserOut])
async def get_all_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/products', response_model=List[ProductOut])
async def gey_all_products():
    query = products.select()
    return await database.fetch_all(query)


@app.get('/orders', response_model=List[OrderOut])
async def gey_all_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model=UserOut)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.get('/products/{product_id}', response_model=ProductOut)
async def get_product(product_id: int):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)


@app.get('/orders/{order_id}', response_model=OrderOut)
async def get_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.post('/users', response_model=UserOut)
async def add_user(user: UserIn):
    password = hashlib.md5(user.password.encode()).hexdigest()
    query = users.insert().values(last_name=user.last_name, first_name=user.first_name, email=user.email,
                                  password=password)
    last_record_id = await database.execute(query)
    return {**user.model_dump(), 'id': last_record_id}


@app.post('/products', response_model=ProductOut)
async def add_product(product: ProductIn):
    query = products.insert().values(products_name=product.products_name, description=product.description,
                                     cost=product.cost)
    last_record_id = await database.execute(query)
    return {**product.model_dump(), 'id': last_record_id}


@app.post('/orders', response_model=OrderOut)
async def add_order(order: OrderIn):
    query = orders.insert().values(user_id=order.user_id, produkts_id=order.produkts_id, data_ord=order.data_ord,
                                   status=order.status)
    last_record_id = await database.execute(query)
    return {**order.model_dump(), 'id': last_record_id}


@app.put('/users/{user_id}', response_model=UserOut)
async def update_user_data(user_id: int, user: UserIn):
    user.password = hashlib.md5(user.password.encode()).hexdigest()
    query = users.update().where(users.c.id == user_id).values(**user.model_dump())
    await database.execute(query)
    return {**user.model_dump(), 'id': user_id}


@app.put('/products/{product_id}', response_model=ProductOut)
async def update_product_data(product_id: int, product: ProductIn):
    query = products.update().where(products.c.id == product_id).values(**product.model_dump())
    await database.execute(query)
    return {**product.model_dump(), 'id': product_id}


@app.put('/orders/{order_id}', response_model=OrderOut)
async def update_order_data(order_id: int, order: ProductIn):
    query = products.update().where(products.c.id == order_id).values(**order.model_dump())
    await database.execute(query)
    return {**order.model_dump(), 'id': order_id}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': f'User {user_id} is deleted'}


@app.delete('/products/{product_id}')
async def delete_product(product_id: int):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': f'Product {product_id} is deleted'}


@app.delete('/orders/{order_id}')
async def delete_user(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': f'Order {order_id} is deleted'}


if __name__ == '__main__':
    # password = hashlib.md5('qazwsxedc'.encode()).hexdigest()
    # dsd = hashlib.md5('qazwsxeuc'.encode()).hexdigest()
    # print(password, dsd)
    ...
