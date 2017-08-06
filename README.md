## RESTful API Generator


RESTful API Generator, autogenerates the RESTful endpoints from the SQL Alchemy models. Works with all major relational databases and MongoDB.



- [Install](#install)
- [Usage](#usage)
- [Credits](#credits)


### Install
```python
pip install flaskrestgen
```

### Usage
```python
'''A sample declarative model using Sqlalchemy'''
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True)
  username = Column(String(50))

#engine instance
engine = create_engine('postgres://user:postgres@localhost:5432/users')
#create tables through your meta data
Base.metadata.create_all(engine)

#now here is the flaskrestgen api at play
from flask import Flask 
from flaskrestgen import RESTApi


app = Flask(__name__)
db_session = sessionmaker(engine)()

#create and instance of flaskrestgen
restApi = RESTApi(app, db_session)
#generates GET, POST, PUT and DELETE for User model
restApi.rest_for(User)
if __name__ == '__main__':
  app.run(host='localhost', port=8000)
  


```
### Endpoints
```python
GET http://localhost:8000/users ("users" being the name of the table)
GET http://localhost:8000/users/<id> 
POST http://localhost:8000/users
    JSON Body: {
        "username" : "newuser"
    }
PUT http://localhost:8000/users/<id>
    JSON Body: {
        "username" : "updatednewuser"
    }
DELETE http://localhost:8000/users/<id>
```


### Credits
Contributors are super welcome!!!!!