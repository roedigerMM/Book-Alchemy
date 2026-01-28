# Book-Alchemy

# README.md

## Library (Flask + SQLAlchemy)

A small library web app built with Flask and SQLAlchemy. It stores data in a local SQLite database file at `./data/library.sqlite`.

### Features
- List all books on the homepage.
- Search by book title or author name.
- Sort by title or author (ascending/descending).
- Add authors and books via simple forms.
- Delete a book (and optionally delete the author if they have no other books).

### Tech stack
- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- SQLite

---

## Getting started

### 1) Clone and create a virtual environment
```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt

