from flask import Flask 
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, Text, Enum, CheckConstraint, DateTime, func, Date, Float
from sqlalchemy import DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session


#create a db session
#create a engine 
engine = create_engine('postgres://user:postgres@localhost:5432/restaurant')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
BASE = declarative_base()
BASE.query = db_session.query_property()

from flaskrestgen import RESTApi

class DineTable(BASE):
    __tablename__ = 'dinetables'
    
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer, nullable=False)
    alias = Column(String(50), unique=True)
    status = Column( Enum('empty', 'unorder', 'order', 'cooking', 'served', name='statuses'))
    
    ##relationship
    dinetable_bills = relationship('Bill', back_populates='dinetable')
    
    

class Payment(BASE):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    p_type = Column(String(100), unique=True)
    
    payment_bills = relationship('Bill', back_populates='payment')
    
class ServiceCharge(BASE):
    __tablename__ = 'servicecharges'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(300),unique=True)
    value = Column(Integer, default=10)
    
    service_charge_bills = relationship('Bill', back_populates='service_charge')
    
class Vat(BASE):
    __tablename__ = 'vats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100),nullable=False, unique=True)
    value = Column(Integer, default=13)
    
    vat_bills = relationship('Bill', back_populates = 'vat')

class Membership(BASE):
    __tablename__ = 'memberships'
    
    id = Column(Integer, primary_key=True)
    m_type = Column(String(50), unique=True, nullable=False)
    discount = Column(Integer, nullable=False, default=0)
    description = Column(Text, default='Description Not Available')
    
    #relationship
    m_customers = relationship('Customer', back_populates='c_membership',cascade='all, delete, delete-orphan')
    


class Customer(BASE):
    __tablename__ = 'customers'
    # we need to keep the name of customer to be unique which is not done yet
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    contact_number = Column(String(16))
    address = Column(String(100), nullable=True)
    gender = Column(String(1),nullable=False)
    age = Column(Integer, CheckConstraint('age>5'))
    email = Column(String(50), default='Email Not Available')
    customer_join_date= Column(DateTime, default=func.now())
    
    #foretign key
    membership_id = Column(Integer, ForeignKey('memberships.id'))
    
    #relatioship
    c_membership = relationship('Membership', back_populates='m_customers')
    
    #bill relationship
    customer_bills = relationship('Bill', back_populates='customer')


class EmployeePosition(BASE):
    __tablename__ = 'employeepositions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(700), default='Description Not Available')
    
    #relationshipo
    p_employees = relationship('Employee', back_populates='e_position', cascade='all, delete, delete-orphan')
    
class Employee(BASE):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    join_date = Column(DateTime, default=func.now())
    salary = Column(Float, CheckConstraint('salary>0.0'), nullable=False)
    contact_number = Column(String(70), nullable=False, unique=True)
    gender = Column(String(1), nullable=False)
    address = Column(String(200), nullable=False, default='No Address Available')
    age = Column(Integer)
    photo_uri = Column(String, nullable=True, default='No photo Available')
    email = Column(String, nullable=True, default = 'No Email Available')
    
    #foreign key
    employee_position_id = Column(Integer, ForeignKey('employeepositions.id'))
    
    #relationship
    e_position = relationship('EmployeePosition', back_populates='p_employees')
    
    #relationship bils
    employee_bills = relationship('Bill', back_populates='employee')
    





class ItemOrder(BASE):
    __tablename__ = 'itemorder'
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(ForeignKey('bills.id'))
    item_id = Column(ForeignKey('items.id'))
    quantity = Column(Integer, nullable=False, default=1)
    order_price = Column(Float, nullable=False)
    order_time_stamp = Column(DateTime, default=func.now())

    #
    bill = relationship('Bill', back_populates='items')
    item = relationship('Item', back_populates='bills')

class ItemCategory(BASE):
    __tablename__ = 'itemcategories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    extra = Column(String(500), nullable=True, default='Not Available')
    #relationship
    c_items = relationship('Item', back_populates='item_category', cascade='all, delete, delete-orphan')

class Item(BASE):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    item_photo_uri = Column(String(500), nullable=True, default='Image URI Not Available')
    description = Column(Text, nullable=True, default ='No Description Available')
    unit_price = Column(Float, nullable=False)
    
    #foreignkey
    item_category_id = Column(Integer, ForeignKey('itemcategories.id'))
    #relationship
    item_category = relationship('ItemCategory', back_populates='c_items')
    
    #many == many relationship #association object pattern
    bills = relationship('ItemOrder', back_populates='item')

    
    
class Bill(BASE):
    __tablename__ = 'bills'
    
    id = Column(Integer, primary_key=True)
    total_price = Column(Float, nullable=False)
    bill_description = Column(String(500), default='Description Not Available')
    on_site = Column(Boolean, default=True)
    bill_time_stamp = Column(DateTime, default=func.now())
    
    #foreign keys
    customer_id = Column(Integer, ForeignKey('customers.id'))
    dinetable_id = Column(Integer, ForeignKey('dinetables.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'))
    payment_id = Column(Integer, ForeignKey('payments.id'))
    vat_id = Column(Integer, ForeignKey('vats.id'))
    service_charge_id = Column(Integer, ForeignKey('servicecharges.id'))
    
    #many==many #assocaition pattern
    items = relationship('ItemOrder',  back_populates='bill')
    
    #relationship
    
    #relationships
    customer = relationship('Customer', back_populates='customer_bills')
    dinetable = relationship('DineTable', back_populates='dinetable_bills')
    employee = relationship('Employee', back_populates='employee_bills')
    payment = relationship('Payment', back_populates='payment_bills')
    vat = relationship('Vat', back_populates='vat_bills')
    service_charge = relationship('ServiceCharge', back_populates='service_charge_bills')
    
    





#assocaitaion table
class PurchaseOrder(BASE):
    __tablename__ = 'purchaseorder'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey('products.id'))
    vendor_id = Column(ForeignKey('vendors.id'))
    
    product_quantity = Column(Integer, nullable=False)
    product_order_price = Column(Float, nullable=False)
    purchase_timestamp = Column(DateTime, default=func.now())
    
    product = relationship('Product', back_populates='vendors')
    vendor = relationship('Vendor', back_populates='products')
    
class ProductCategory(BASE):
    __tablename__ = 'productcategories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(400), nullable=False, unique=True)
    extra = Column(String(500), nullable=True, default='Not Available')
    #relationship
    c_products = relationship('Product', back_populates='product_category', cascade='all, delete, delete-orphan')
    
class Product(BASE):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    unit_price = Column(Float)
    product_category_id = Column(Integer, ForeignKey('productcategories.id'))
    #relationship
    product_category = relationship('ProductCategory', back_populates='c_products')
    
    #many == many relationship #associatyion object pattern
    vendors = relationship('PurchaseOrder', back_populates='product')
    
class Vendor(BASE):
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    address1 = Column(String, nullable=False)
    address2 = Column(String, nullable=True)
    contact = Column(Integer, nullable = False)
    country = Column(String)
    website = Column(String)
    email = Column(String)
    agent_name = Column(String)
    agent_number = Column(Integer)
    agent_address = Column(String)
    
    ##many to many relationship
    products = relationship('PurchaseOrder', back_populates='vendor')
    



#now create and app instace
app = Flask(__name__)

api = RESTApi(app, db_session, validation_file='validation.json')
api.rest_for(DineTable)
api.rest_for(Vendor)
api.rest_for(Product, extract=['product_category'], extractfor_resources = ['product_category'])
api.rest_for(ProductCategory, extract=['c_products'], relationship=True)
api.rest_for(PurchaseOrder)
api.rest_for(Bill)
api.rest_for(Item, extractfor_resources=['item_category'])
api.rest_for(ItemCategory, relationship=True)
api.rest_for(ItemOrder)
api.rest_for(Employee, extract=['e_position'])
api.rest_for(EmployeePosition, extract=['p_employees'])
api.rest_for(Customer)
api.rest_for(Payment)
api.rest_for(ServiceCharge)
api.rest_for(Vat)
api.rest_for(Membership)



def init_db():
    BASE.metadata.create_all(engine)


if __name__ == '__main__':
    app.run('localhost', 6000, debug=True)


