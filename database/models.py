from os import getenv
from dotenv import load_dotenv

from sqlalchemy.orm import DeclarativeBase, Mapped, Session, relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer, BigInteger, Float, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy import create_engine
from unicodedata import category

load_dotenv()

DB_USER=getenv('DB_USER')
DB_PASSWORD=getenv('DB_PASSWORD')
DB_ADDRESS=getenv('DB_ADDRESS')
DB_NAME=getenv('DB_NAME')
DB_DEBUG=getenv('DB_DEBUG')

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}', echo=f'{DB_DEBUG}')

class Base(DeclarativeBase):
    pass


class Users(Base):
    """База пользователей"""
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(String(11), nullable=True)

    cards: Mapped[int] = relationship('Carts', back_populates='user_cart')

    def __str__(self):
        return self.name


class Carts(Base):
    """Временная корзина покупателя, используется до кассы (отложенный чек)"""
    __tablename__ = 'carts'
    id: Mapped[int] = mapped_column(primary_key=True)
    total_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[float] = mapped_column(Float, default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)

    user_cart: Mapped[Users] = relationship(back_populates='carts')
    finally_id: Mapped[int] = relationship('FinallyCarts', back_populates='user_cart')

    def __str__(self):
        return str(self.id)


class FinallyCarts(Base):
    """Окончательная корзина пользователя, возле кассы"""
    __tablename__ = 'finally_carts'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Float, default=0)
    final_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.id'))

    user_cart: Mapped[Carts] = relationship(back_populates='finally_id')

    __table_args__ = UniqueConstraint('cart_id', 'product_name')

    def __str__(self):
        return str(self.id)


class Categories(Base):
    """Категории продуктов"""
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(20), unique=True)

    # products: Mapped['Products'] = relationship('product_category')
    products = relationship('Products', back_populates='product_category')

    def __str__(self):
        return self.category_name


class Products(Base):
    """Продукты"""
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String(100))
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    product_category: Mapped[Categories] = relationship('products')

    def __str__(self):
        return self.product_name



def main():
    Base.metadata.create_all(engine)
    categories = ('category_1: Шерсть', 'category_2: Хлопок', 'category_3: Бархат', 'Плащевая', 'Шелк')
    products = (
        (1, '9/21/2/П Синий', 2000, 'Шерсть 70%, п/а 30%', 'image_path_category_1'),
        (1, 'Твид: Арт. 16976/0220', 3000, 'Ширина: 140 см; Состав: 80% ШЕРСТЬ, 20% ПОЛИЭСТЕР; Производитель: Италия', 'image_path_category_1'),
        (1, 'Твид: Арт. 40/21/2/Ш', 4000, 'Ширина: 140 см; Состав: 60% ШЕРСТЬ, 20% ВИСКОЗА, 20% ПОЛИЭСТЕР; Производитель: Италия', 'image_path_category_1'),
        (2, 'в клетку: Арт. FZG2021 #7 /22/1', 5000, 'Ширина: 140 см; Состав: 100% ХЛОПОК; Производитель: Италия', 'image_path_category_2'),
        (2, 'однотонный: Арт. JTC-5141 #18-3929', 2500, 'Ширина: 140 см; Состав: 100% ХЛОПОК; Производитель: Италия', 'image_path_category_2'),
        (2, 'в полоску: Арт. STRIBE NEW2#6 s.cotton /03/21/', 2700, 'Ширина: 140 см; Состав: 100% ХЛОПОК; Производитель: Италия', 'image_path_category_2'),
    )

    with Session(engine) as session:
        for category_name in categories:
            query = Categories(category_name=category_name)
            session.add(query)
            session.commit()

        for product in products:
            query = Products(
                category_id=product[0],
                category_name=product[1],
                price=product[2],
                description=product[3],
                image=product[4],
            )
            session.add(query)
            session.commit()


if __name__ == '__main__':
    main()



# https://stackoverflow.com/questions/54646044/sqlalchemy-tablename-as-a-variable
# Область действия вашего Stock класса ограничена create_models функцией. Чтобы создать объект этого класса вне функции,
# вы можете вернуть класс из функции и затем использовать его.
#
# взгляните на решение ниже:
# def create_models(tablename):
#
#     class Stock(Base):
#
#         __tablename__ = tablename
#
#         timestamp = Column(String, primary_key=True)
#         ltp = Column(String)
#
#         def __init__(self, timestamp, ltp):
#             self.timestamp = timestamp
#             self.ltp = ltp
#     return Stock #return the class
#
# Stock = create_models('ABCD')
# tick = Stock('2019-02-12 09:15:00', '287')
# Более подробную информацию об области действия см. в руководстве по области действия Python
# (https://www.geeksforgeeks.org/namespaces-and-scope-in-python/).