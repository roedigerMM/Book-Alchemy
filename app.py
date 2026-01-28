# app.py
"""
Library web app (Flask + SQLAlchemy).

Routes:
- / : List/search/sort books.
- /add_author : Create an author (GET shows form, POST saves).
- /add_book : Create a book (GET shows form, POST saves).
- /book/<int:book_id>/delete : Delete a book (POST only).

Database:
- SQLite file stored in ./data/library.sqlite
"""

import os
from datetime import datetime

from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from data_models import db, Author, Book

# Resolve the absolute project directory so the SQLite path works regardless of where
# the app is started from (e.g., different working directories).
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configure SQLAlchemy to use a local SQLite database file.
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Bind the SQLAlchemy instance (defined in data_models.py) to this Flask app.
db.init_app(app)

# One-time initialization helper: create tables based on the models in data_models.py.
# Run once, then comment out to avoid accidentally recreating tables.
# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    """Render the library homepage.

    Features:
    - Search by book title or author name using the `q` query parameter.
    - Sort by title or author using `sort` (title|author).
    - Sort direction using `order` (asc|desc).
    - Optional status message via `msg` query parameter (used after actions like delete).

    Returns:
        Rendered home.html template with the current list of books and UI state.
    """
    # Read UI parameters (with defaults) from the query string.
    sort_option = request.args.get("sort", "title")
    order_option = request.args.get("order", "asc")
    search_query = request.args.get("q", "").strip()
    message = request.args.get("msg")

    # Use joinedload so accessing `book.author` in the template does not trigger
    # an extra database query per book (avoids the N+1 query problem).
    query = Book.query.options(joinedload(Book.author))

    # Join Author because we want to filter/sort by author attributes too.
    query = query.join(Author)

    # Apply search only if the user typed something. `ilike` is case-insensitive.
    if search_query:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search_query}%"),
                Author.name.ilike(f"%{search_query}%"),
            )
        )

    # Map the UI "sort" option to the actual SQLAlchemy column to order by.
    sort_column = Author.name if sort_option == "author" else Book.title

    # Apply ascending/descending order.
    query = query.order_by(sort_column.desc() if order_option == "desc" else sort_column.asc())

    books = query.all()

    return render_template(
        "home.html",
        books=books,
        current_sort=sort_option,
        current_order=order_option,
        search_query=search_query,
        message=message,
    )


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Create a new Author.

    GET:
        Render the form.
    POST:
        Validate required fields, parse dates, insert into the database.

    Notes:
        - birth_date is required and must be YYYY-MM-DD.
        - date_of_death is optional and, if provided, must be YYYY-MM-DD.
    """
    success_message = None
    error_message = None

    if request.method == "POST":
        # Read form fields.
        name = request.form.get("name")
        birth_date = request.form.get("birth_date")  # expected YYYY-MM-DD
        date_of_death = request.form.get("date_of_death")

        # Basic validation.
        if not name or not birth_date:
            error_message = "Name and birth date are required."
        else:
            # Convert string inputs into actual Python date objects.
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            date_of_death = (
                datetime.strptime(date_of_death, "%Y-%m-%d").date()
                if date_of_death
                else None
            )

            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            success_message = "Author added successfully!"

    return render_template(
        "add_author.html",
        success_message=success_message,
        error_message=error_message,
    )


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Create a new Book.

    GET:
        Render the form (including list of authors to choose from).
    POST:
        Validate required fields, convert numeric fields, insert into the database.

    Required fields:
        title, publication_year, isbn, author_id
    """
    success_message = None
    error_message = None

    # Used to populate an author selection widget in the template.
    authors = Author.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")
        isbn = request.form.get("isbn")

        if not title or not publication_year or not author_id or not isbn:
            error_message = "Title, publication year, ISBN and author id are required."
        else:
            # Convert incoming form strings to the types expected by the model.
            new_book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(publication_year),
                author_id=int(author_id),
            )
            db.session.add(new_book)
            db.session.commit()
            success_message = "Book added successfully!"

    return render_template(
        "add_book.html",
        authors=authors,
        success_message=success_message,
        error_message=error_message,
    )


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int):
    """Delete a single book.

    This endpoint accepts POST requests only to prevent accidental deletions via
    link clicks or page loads.

    Behavior:
    - If the book does not exist, redirect back to home with a friendly message.
    - If the book exists, delete it.
    - If the book's author has no other books left, also delete the author.

    Args:
        book_id: Primary key of the book to delete.

    Returns:
        Redirect response to the homepage (/) with a `msg` query parameter.
    """
    # Look up the book by primary key.
    book = Book.query.get(book_id)

    # If it was already deleted (or never existed), do not crash—just redirect.
    if book is None:
        return redirect(url_for("home", msg="Book not found (already deleted)."))

    # Keep the title for the user message after deletion.
    title = book.title

    # Cache author info before deleting the book row.
    author = book.author
    author_id = book.author_id

    # Count other books by the same author (excluding the current book).
    remaining = Book.query.filter(Book.author_id == author_id, Book.id != book_id).count()

    # Delete the book.
    db.session.delete(book)

    # Optional cleanup: remove the author if they have no books left in the library.
    if remaining == 0 and author is not None:
        db.session.delete(author)

    db.session.commit()
    return redirect(url_for("home", msg=f'Deleted "{title}" successfully.'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
