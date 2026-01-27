from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)

#Create the tables defined in data_models.py, Only run when tables are not created yet. Comment out otherwise!
with app.app_context():
  db.create_all()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)