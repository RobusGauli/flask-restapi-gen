## RESTful API Generator


RESTful API Generator, autogenerates the RESTful endpoints from the SQL Alchemy models. Works with all major relational databases and MongoDB.




- [Usage](#usage)
- [Credits](#credits)




### Usage
```python
from flask import Flask 
from restfulapigen import RESTApi
from models import (
    Post,
    Comment,
    Profile
)
from my_session import db_session
app = Flask(__name__)

my_api = RESTApi(app, db_session)
#generate all GET, PUT, POST, DELETE methods for model
my_api.rest_for(Comment)

#you can also apply specific method for resource 
#generate 'GET' support for Person model
my_api.get_for(Person)
#generate 'UPDATE' support for Person model
my_api.update_for(Person)
#generate 'GET' support for Comment model
my_api.get_for(Comment)

#BOOM!! You now have rest api endpoints

```



### Credits
Contributors are super welcome!!!!!