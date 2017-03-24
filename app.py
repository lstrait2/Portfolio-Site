from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# initialize flask app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/lance/Assignment3.1/app/database/portfolio.db'

# set-up database
db = SQLAlchemy(app)


