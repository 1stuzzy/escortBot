from tgbot.models.models import User, Product, PaymentMethod, Subscription, Worker, Order
from sqlalchemy import and_, or_
from datetime import datetime

async def add_user(telegram_id: int, worker_id: int, username: str):
    user = User()

    user.TelegramID = telegram_id
    user.WorkerID = worker_id
    user.Username = username

    await user.create()
    
    return user.ID

async def get_user(user_id: int):
    return await User.query.where(User.TelegramID == user_id).gino.first()

async def update_user(user_id: int, **kwargs):
    user = await get_user(user_id)

    if user:
        await user.update(**kwargs).apply()

    return True

async def add_product(worker_id: int,
                        is_default: bool,
                        city_number: int,
                        name: str,
                        years: int,
                        cost: int,
                        desc: str,
                        services: str,
                        photos: list):
    
    product = Product()

    product.WorkerID = worker_id
    product.IsDefault = is_default
    product.CityNumber = city_number
    product.Name = name
    product.Years = years
    product.Cost = cost
    product.CostPerTwoHours = int((cost * 2) - (cost * 2 * 0.02))
    product.CostPerNight = (cost * 4) + 1200
    product.Description = desc
    product.Services = services
    product.Photos = photos
    product.ChannelCost = 50000

    await product.create()

    return product.ID

async def get_default_productions(city_number: int):
    return await Product.query.where(
        and_(
            Product.CityNumber == city_number,
            Product.IsDefault
        )
    ).order_by(Product.ID).gino.all()

async def get_worker_productions(city_number: int,
                                worker_id: int):
    worker = await get_worker(worker_id)

    if worker:
        return await Product.query.where(
            and_(
                Product.CityNumber == city_number,
                Product.WorkerID == worker_id, 
                Product.IsDefault == False
            )
        ).order_by(Product.ID).gino.all()

    return []

async def get_page_products_by_city(city_number: int,
                                worker_id: int,
                                page: int):

    if worker_id:
        worker = await get_worker(worker_id)

        if worker:
            return await Product.query.where(
                and_(
                    Product.CityNumber == city_number,
                    or_(
                        and_(Product.WorkerID == worker_id, Product.IsDefault == False),
                        and_(worker.escort_default_productions_1 == True, city_number == 0, Product.IsDefault == True),
                        and_(worker.escort_default_productions_2 == True, city_number == 1, Product.IsDefault == True)
                    )
                )
            ).offset(page * 10).order_by(Product.ID).gino.all()

    return await Product.query.where(
        and_(
            Product.CityNumber == city_number,
            Product.IsDefault
        )
    ).offset(page * 10).order_by(Product.ID).gino.all()

async def get_all_products_by_city(city_number: int,
                                worker_id: int):

    if worker_id:
        worker = await get_worker(worker_id)

        if worker:
            return await Product.query.where(
                and_(
                    Product.CityNumber == city_number,
                    or_(
                        and_(Product.WorkerID == worker_id, Product.IsDefault == False),
                        (worker.escort_default_productions_1 == True and city_number == 0 and Product.IsDefault == True),
                        (worker.escort_default_productions_2 == True and city_number == 1 and Product.IsDefault == True)
                    )
                )
            ).gino.all()

    return await Product.query.where(
        and_(
            Product.CityNumber == city_number,
            Product.IsDefault
        )
    ).gino.all()

async def get_product(product_id: int):
    return await Product.query.where(Product.ID == product_id).gino.first()

async def add_method(name: str, symbol: str, currency: str, rate: float, is_crypto: bool):
    method = PaymentMethod()

    method.Name = name
    method.Symbol = symbol
    method.CurrencyName = currency
    method.CurrencyRate = rate
    method.IsCrypto = is_crypto

    await method.create()

    return method.ID

async def get_methods():
    return await PaymentMethod.query.where(PaymentMethod.Enable).order_by(PaymentMethod.ID).gino.all()

async def get_method(method_id: int):
    return await PaymentMethod.query.where(PaymentMethod.ID == method_id).gino.first()

async def add_sub(name: str, desc: str, cost: int):
    sub = Subscription()

    sub.Name = name
    sub.Desc = desc
    sub.Cost = cost

    await sub.create()

    return sub.ID

async def get_sub(id: int):
    return await Subscription.query.where(Subscription.ID == id).gino.first()

async def get_all_subs():
    return await Subscription.query.order_by(Subscription.ID).gino.all()

async def get_worker(user_id: int):
    return await Worker.query.where(Worker.user_id == user_id).gino.first()

async def add_order(user_id: int,
                    product_id: int,
                    additionals: list,
                    tariff: int,
                    book_info: str):
    
    order = Order()

    order.UserID = user_id
    order.ProductID = product_id
    order.AdditionalServices = additionals
    order.Tariff = tariff
    order.BookInfo = book_info
    order.Date = datetime.now()

    order.Status = 0

    await order.create()

    return order.ID

async def get_user_active_orders(user_id: int):
    return await Order.query.where(
        and_(
            Order.UserID == user_id,
            Order.Status == 0
        )
    ).gino.all()

async def get_user_confirmed_orders(user_id: int):
    return await Order.query.where(
        and_(
            Order.UserID == user_id,
            Order.Status == 2
        )
    ).gino.all()

async def get_order(order_id: int):
    return await Order.query.where(Order.ID == order_id).gino.first()