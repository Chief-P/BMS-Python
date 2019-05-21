from tables import *

# session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import current_time
from sqlalchemy import desc

# exceptions
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

# UI
import os
import getpass

# Secure Type Conversions
def ints(s):
    if s == '':
        return None
    else:
        return int(s)

def floats(s):
    if s == '':
        return None
    else:
        return float(s)

def strs(s):
    if s == '':
        return None
    else:
        return s

class BMS:
    """
    Book Management System
    """
    def __init__(self):
        passwd = getpass.getpass('Password of root: ')
        # [database]+[driver]://username:password@address:port/dbname
        engine = create_engine('mysql+mysqlconnector://root:%s@localhost:3306/bms' %passwd)

        # create tables for all subclasses
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine) # create a session maker
        self.session = Session()
        if self.session.query(Manager).count() == 0: # create manager if not exists
            self.insert_manager()

    def insert_manager(self):
        print('$ Manager Register')
        mno = input('ID: ')
        name = input('Name: ')
        password = input('Password: ')
        phone = input('Phone: ')
        self.session.add(Manager(mno=mno, name=name, password=password, phone=phone))
        self.session.commit()

    def login(self):
        print('$ Manager Login')
        self.mno = input('ID: ')
        query = self.session.query(Manager).filter(Manager.mno == self.mno)
        try:
            query.one()
            password = input('Password: ')
            if query.first().password != password:
                print("Wrong Password")
                exit(0)
        except NoResultFound:
            print('ID Not Found')
            exit(0)

    def get_command(self):
        os.system('cls')
        print('$ Services')
        print('1 Insert Book')
        print('2 Query Book')
        print('3 Borrow Book')
        print('4 Return Book')
        print('5 Insert Card')
        print('6 Drop Card')
        print('7 Insert Batch')
        print('0 Exit')
        cmd = input('> ')
        while not cmd.isdigit():
            cmd = input('> ')
        return int(cmd)

    def get_book(self):
        """
        @return: map of attributes
        """
        bno = strs(input('bno: '))
        genre = strs(input('genre: '))
        title = strs(input('title: '))
        press = strs(input('press: '))
        year = ints(input('year: '))
        author = strs(input('author: '))
        price = floats(input('price: '))
        total = ints(input('total: '))
        stock = ints(input('stock: '))
        return Book(bno=bno, genre=genre, title=title, press=press, year=year, author=author, price=price, total=total, stock=stock)

    def insert_book(self, book):
        try:
            self.session.add(book)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            print("bno %s: Duplicated" % book.bno)

    def insert_batch(self):
        try:
            with open('book_list.txt', 'r') as f:
                for line in f:
                    attrs = (line.strip())[1:-1].split(',')
                    attrs = [attr.strip() for attr in attrs]
                    book = Book(bno=attrs[0], genre=attrs[1], title=attrs[2], press=attrs[3], year=attrs[4], author=attrs[5], price=attrs[6], total=attrs[7], stock=attrs[7])
                    self.insert_book(book)
        except FileNotFoundError:
            print('File Not Found: book_list.txt')
            
    def query_book(self):
        query = self.session.query(Book)
        bno = input('bno: ')
        if bno != '':
            query = query.filter(Book.bno == bno)

        genre = input('genre: ')
        if genre != '':
            query = query.filter(Book.genre == genre)

        title = input('title: ')
        if title != '':
            query = query.filter(Book.title.like('%%%s%%' % title))

        press = input('press: ')
        if press != '':
            query = query.filter(Book.press == press)

        year = input('year: ') # interval
        if year != '':
            if ',' not in year:
                query = query.filter(Book.year == int(year))
            else:
                interval = year.split(',')
                query = query.filter(Book.year >= int(interval[0]))
                query = query.filter(Book.year <= int(interval[1]))

        author = input('author: ')
        if author != '':
            query = query.filter(Book.author == author)

        price = input('price: ') # interval
        if price != '':
            if ',' not in price:
                query = query.filter(Book.price == float(price))
            else:
                interval = price.split(',')
                query = query.filter(Book.price >= float(interval[0]))
                query = query.filter(Book.price <= float(interval[1]))

        total = input('total: ')
        if total != '':
            query = query.filter(Book.total == int(total))

        stock = input('stock: ')
        if stock != '':
            query = query.filter(Book.stock == int(stock))
        
        print('Book(bno, genre, title, press, year, author, price, total, stock)')
        i = 1
        for book in query[:50]: # show 50 results at most
            print('%2d' % i, book)
            i += 1

    def check_card(self, cno):
        query = self.session.query(Card).filter(Card.cno == cno)
        if query.count() == 0:
            return False
        else:
            return True

    def get_borrow(self, cno): # and show
        query = self.session.query(Book).join(Borrow).filter(Borrow.cno == cno).filter(Borrow.return_date == None)
        print('Books_Borrowed(bno, genre, title, press, year, author, price, total, stock)')
        i = 1
        for book in query:
            print('%2d' % i, book)
            i += 1
        return query

    def borrow_book(self):
        cno = input('cno: ')
        if self.check_card(cno):
            self.get_borrow(cno)
            bno = input('bno: ')
            query = self.session.query(Book).filter(Book.bno == bno)
            if query.count() != 0:
                book = query.first()
                if book.stock > 0:
                    book.stock -= 1
                    borrow = Borrow(bno=bno, cno=cno, borrow_date=current_time(), return_date=None, mno=self.mno)
                    self.session.add(borrow)
                    self.session.commit()
                else:
                    print('Out of Stock')
                    borrow = self.session.query(Borrow).filter(Borrow.bno == bno).order_by(desc(Borrow.return_date)).first()
                    print('The last return date: %s' % borrow.return_date)
            else:
                print('Book Not Found')
        else:
            print('Card Not Found')

    def return_book(self):
        cno = input('cno: ')
        if self.check_card(cno):
            borrowed_books = self.get_borrow(cno)
            borrowed_bnos = [book.bno for book in borrowed_books]
            bno = input('bno: ')
            if bno in borrowed_bnos:
                book = self.session.query(Book).filter(Book.bno == bno).first()
                book.stock += 1
                # if cno borrowed bno twice, then return one of them
                borrow = self.session.query(Borrow).filter(Borrow.cno == cno).filter(Borrow.bno == bno).filter(Borrow.return_date == None).first()
                borrow.return_date = current_time()
                self.session.commit()
            else:
                print('Invalid Book Number')
        else:
            print('Card Not Found')

    def insert_card(self):
        cno = input('cno: ')
        name = input('name: ')
        department = input('department: ')
        genre = input('genre: ')
        card = Card(cno=cno, name=name, department=department, genre=genre)
        try:
            self.session.add(card)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            print('cno %s: Duplicated' % card.cno)

    def drop_card(self):
        cno = input('cno: ')
        if self.check_card(cno):
            card = self.session.query(Card).filter(Card.cno == cno).first()
            self.session.delete(card)
            self.session.commit()
        else:
            print('Card Not Found')

    def run(self):
        self.login()
        cmd = self.get_command()
        while cmd != 0:
            if cmd == 1:
                self.insert_book(self.get_book())
            elif cmd == 2:
                self.query_book()
            elif cmd == 3:
                self.borrow_book()
            elif cmd == 4:
                self.return_book()
            elif cmd == 5:
                self.insert_card()
            elif cmd == 6:
                self.drop_card()
            elif cmd == 7:
                self.insert_batch()
            input('Press Enter to Continue...')
            cmd = self.get_command()
        print('logout')


if  __name__ == "__main__":
    bms = BMS()
    bms.run()