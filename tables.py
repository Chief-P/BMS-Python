# table related
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base() # declarative base

class Book(Base):
    __tablename__ = 'book'

    bno = Column(String(20), primary_key=True)
    genre = Column(String(50))
    title = Column(String(100))
    press = Column(String(100))
    year = Column(Integer)
    author = Column(String(50))
    price = Column(Numeric(7, 2))
    total = Column(Integer)
    stock = Column(Integer)

    borrow = relationship('Borrow', cascade='all, delete', backref='book')

    def __repr__(self):
        return '(%s, %s, %s, %s, %s, %s, %s, %s, %s)' % (self.bno, self.genre, self.title, self.press, self.year, self.author, self.price, self.total, self.stock)

class Card(Base):
    __tablename__ = 'card'

    cno = Column(String(20), primary_key=True)
    name = Column(String(50))
    department = Column(String(100))
    genre = Column(Enum('T', 'S'))

    borrow = relationship('Borrow', cascade='all, delete', backref='card')

class Manager(Base):
    __tablename__ = 'manager'

    mno = Column(String(20), primary_key=True)
    name = Column(String(50))
    password = Column(String(50))
    phone = Column(String(20))

    borrow = relationship('Borrow', cascade='all, delete', backref='manager')

class Borrow(Base):
    __tablename__ = 'borrow'

    bno = Column(String(20), ForeignKey('book.bno'), primary_key=True)
    cno = Column(String(20), ForeignKey('card.cno'), primary_key=True)
    borrow_date = Column(DateTime, primary_key=True)
    return_date = Column(DateTime)
    mno = Column(String(20), ForeignKey('manager.mno'))

    def __repr__(self):
        return '(%s, %s, %s, %s, %s)' % (self.bno, self.cno, self.borrow_data, self.return_date, self.mno)

# def get_password():
#     """
#     get the password to the root of MySQL
#     ask for the password if not stored
#     """
#     try:
#         with open('.pswd', 'r') as f:
#             passwd = f.read()
#     except FileNotFoundError:
#         passwd = input("Password of root: ")
#         with open('.pswd', 'w') as f:
#             f.write(passwd)
#     return passwd