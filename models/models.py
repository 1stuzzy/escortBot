from sqlalchemy import Column, Integer, BigInteger, JSON, DateTime, String, Boolean, Float
from tgbot.models.database import db

class User(db.Model):
    __tablename__ = 'escort_users'
    
    ID = Column(Integer, primary_key = True, autoincrement = True, unique = True)
    TelegramID = Column(BigInteger, unique = True)
    WorkerID = Column(BigInteger, nullable = True)
    Username = Column(String(128), nullable = True)

    SelectedCity = Column(Integer, nullable = True, default = None)
    Cities = Column(JSON, default = [])

    Rating = Column(Integer, default = 5)

class Product(db.Model):
    __tablename__ = 'escort_productions'

    ID = Column(Integer, primary_key = True, autoincrement = True, unique = True)
    WorkerID = Column(BigInteger, nullable = True)
    IsDefault = Column(Boolean, default = False)
    CityNumber = Column(Integer, default = 0)

    Name = Column(String(128))
    Years = Column(Integer)

    Cost = Column(Integer)
    CostPerTwoHours = Column(Integer)
    CostPerNight = Column(Integer)

    Description = Column(String(512))
    Services = Column(String(512))
    AdditionalServices = Column(JSON, default = []) # Доп. Услуги. Структура: [{"name": "Название", "cost": Цена}, ...]

    Photos = Column(JSON, default = []) # Фотографии. Структура: [link, link, link, ...]

    ChannelCost = Column(Integer, default = 0)
    ChannelLink = Column(String(256), default = None, nullable = True)

class PaymentMethod(db.Model):
    __tablename__ = 'escort_methods'

    ID = Column(Integer, primary_key = True, autoincrement = True, unique = True)

    Name = Column(String(128))
    Requisits = Column(String(1024), default = "Не установлено")
    Symbol = Column(String(12))

    CurrencyName = Column(String(12))
    CurrencyRate = Column(Float)

    Enable = Column(Boolean, default = True)
    IsCrypto = Column(Boolean, default = False)

class Subscription(db.Model):
    __tablename__ = 'escort_subscriptions'

    ID = Column(Integer, primary_key = True, autoincrement = True, unique = True)

    Name = Column(String(128))
    Desc = Column(String(1024))
    Cost = Column(Integer)

class Worker(db.Model):
    __tablename__ = 'users'

    user_id = Column(BigInteger)

    escort_default_productions_1 = Column(Boolean, default = True)
    escort_default_productions_2 = Column(Boolean, default = True)
    escort_city_change = Column(Boolean, default = True)
    escort_notification = Column(Boolean, default = True)
    escort_profit = Column(Integer, default = 0) # если надо будет, то вот

class Order(db.Model):
    __tablename__ = 'escort_orders'

    ID = Column(Integer, primary_key = True, autoincrement = True, unique = True)
    UserID = Column(BigInteger)

    ProductID = Column(Integer)
    AdditionalServices = Column(JSON, default = [])
    Tariff = Column(Integer) # 1,2 часа и ночь
    BookInfo = Column(String(1024), nullable = True) # инфа о бронировании
    Date = Column(DateTime)

    Status = Column(Integer) # в ожидании / отклонен / одобрен