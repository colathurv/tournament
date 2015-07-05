# category_database_setup.py -- Implements ORM to create Category
# and item objects and helper functions that help create
# instances of these. The helper functions read a CSV file that 
# to populate the initial set of data and provide a jump start
# in terms of looking at the category web application with some 
# meaningful data to begn with.
# Author :: Colathur Vijayan ["VJN"]
#

import os
import sys
import string
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base() 

class Category(Base):
    """The object representation of the Category Table"""
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
 
class Item(Base):
    """The object representation of the Item Table along with Relational Dependencies"""
    __tablename__ = 'item'

    name = Column(String(120), nullable = False)
    id = Column(Integer, primary_key = True)
    sku = Column(String(80), nullable=False)
    description = Column(String(500))
    price = Column(String(8))
    image = Column(String(100))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    modified_on = Column(DateTime, default=func.now())
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
                 'name'         : self.name,
                 'description'         : self.description,
                 'id'         : self.id,
                 'sku'         : self.sku
           } 
   
def cleanUp():
    """Helper function that will drop these tables in the DB,so as to start on a clean slate"""
    engine = create_engine('sqlite:///categoryitem.db')
    connection = engine.connect() 
    print "connected"
    trans = connection.begin() 
    try: 
        connection.execute("drop table if exists item")
        connection.execute("drop table if exists category")
        trans.commit() 
        connection.close()
        print "tables dropped"
    except: 
        trans.rollback()
        connection.close()
        print "error while dropping tables .." 

def popCategories(): 
    """Helper function that populates test categories from a CSV file"""
    engine = create_engine('sqlite:///categoryitem.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    # Add categories from file
    categories = []
    item_list = open("items.csv")
    for i in item_list:
        if not i.startswith("#"):
            arr = string.split(i,",")
            if arr[0] not in categories:
                categories.append(arr[0])
                myCategory = Category(name = arr[0])
                session.add(myCategory)
                session.commit()
    session.close()
    
def popItems(): 
    """Helper function that populates test items from a CSV file"""
    engine = create_engine('sqlite:///categoryitem.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    # Add items from file
    item_list = open("items.csv")
    for i in item_list:
        if not i.startswith("#"):
            item = string.split(i,",")
            category = session.query(Category).filter_by(name = item[0]).one()
            print "id is", category.id
	    newItem = Item(name = item[2], sku = item[1], description = item[5], price = item[4], category_id = category.id, image = item[3] )
            session.add(newItem)
            session.commit()
    session.close()
	        
def readCategoriesandItems():
    """Helper function that read all categoris and items from the database"""
    engine = create_engine('sqlite:///categoryitem.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    categories = session.query(Category).all()
    print "In here .."
    for c in categories:
        print "---------------"
        print "category id = ",c.id
        print "categor name = ",c.name
	try:
	    items = session.query(Item).filter_by(category_id = c.id)
	    for i in items:
	        print "item id =", i.id
	        print "item name=", i.name
	        print "item description =", i.description
	        print "item price =", i.price
	        print "item image =", i.image
	        print "item last modified =", i.modified_on
        except:
	    print "No items to print for this category.."       	               
        session.close()
  

def main():
    """Calls all the functions in a sequence so we can start on a clean slate"""
    cleanUp()
    engine = create_engine('sqlite:///categoryitem.db')
    Base.metadata.create_all(engine)
    popCategories()
    popItems()
    readCategoriesandItems()
    
if __name__ == '__main__':
    main()