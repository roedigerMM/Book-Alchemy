# Library (Flask + SQLAlchemy)

A small Flask web app to manage a personal library (authors + books) using SQLAlchemy and a local SQLite database. [file:1]

## Features

-   Homepage lists all books, with search and sorting. [file:1]
-   Add authors and books via simple HTML forms. [file:1]
-   SQLite database stored at `./data/library.sqlite`. [file:1]
-   Modern UI styling via a shared CSS file (recommended: `static/style.css`) using flexbox cards and a toolbar.

## Tech stack

-   Flask (server + routing + templates). [file:1]
-   SQLAlchemy (ORM) via your `db`, `Author`, and `Book` models. [file:1]

## Project structure

Recommended layout:

```text
.
├── app.py
├── data_models.py
├── requirements.txt
├── README.md
├── data/
│   └── library.sqlite
├── static/
│   └── style.css
└── templates/
    ├── home.html
    ├── add_author.html
    └── add_book.html

Setup
1) Create a virtual environment and install dependencies

python -m venv .venv
# Windows: .venvScriptsactivate
source .venv/bin/activate

pip install -r requirements.txt

2) Create the database folder

mkdir -p data

3) Initialize the database tables (first run only)
Your  app.py  contains a commented-out  db.create_all()  block for creating tables. file:1
Option A (recommended): run it from a Python shell:

python

from app import app
from data_models import db

with app.app_context():
    db.create_all()

Option B: temporarily uncomment the  db.create_all()  block in  app.py , run the app once, then comment it again. file:1
Run the application
Start the dev server:

python app.py

The app runs on port  5001  (debug mode enabled in your current config). file:1
Open:
	•	http://127.0.0.1:5001/
Routes
	•	 GET /  — Homepage (list/search/sort). file:1
	•	 GET, POST /add_author  — Add an author. file:1
	•	 GET, POST /add_book  — Add a book. file:1
UI styling (modern design)
	•	Put your stylesheet in  static/style.css .
	•	Link it from templates using:

<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

Notes
	•	The homepage search uses a case-insensitive filter ( ilike ) across book titles and author names. file:1
	•	Sorting can be done by book title or author name, ascending or descending.
```