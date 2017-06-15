from setuptools import setup
setup(
  name = 'flaskrestgen',
  packages = ['flaskrestgen'], # this must be the same as the name above
  version = '0.3',
  description = 'A restful API generator for flask/sqlalchemy declarative models.',
  author = 'Robus Gauli',
  author_email = 'robusgauli@gmail.com',
  url = 'https://github.com/RobusGauli/flask-restapi-gen', # use the URL to the github repo
  download_url = 'https://github.com/RobusGauli/flask-restapi-gen/archive/0.3.tar.gz', # I'll explain this in a second
  keywords = ['flask', 'restapi', 'restful', 'restgenerator'], # arbitrary keywords
  classifiers = [],
)