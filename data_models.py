# data_models.py
"""
SQLAlchemy models for the Library app.

Models:
- Author: Stores basic author metadata and links to their books.
- Book: Stores book metadata and references an Author via a foreign key.

The `db` object is initialized in app.py via `db.init_app(app)`.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """Author table.

    Columns:
        id: Integer primary key.
        name: Author name (required).
        name_normalized: Author name (normalized lower-case; unique).
        birth_date: Date of birth (required).
        date_of_death: Date of death (optional).

    Relationships:
        books: Collection of Book instances written by this author.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    name_normalized = db.Column(db.String(255), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", back_populates="author")

    def __repr__(self) -> str:
        """Return a debug-friendly representation (useful in logs and the Python shell)."""
        return (
            f"Author(name={self.name!r}, id={self.id}, "
            f"birth_date={self.birth_date}, date_of_death={self.date_of_death})"
        )

    def __str__(self) -> str:
        """Return a human-friendly string representation (useful for UI output)."""
        return self.name


class Book(db.Model):
    """Book table.

    Columns:
        id: Integer primary key.
        isbn: ISBN string (required; unique).
        title: Book title (required).
        publication_year: Publication year (required).
        author_id: Foreign key referencing Author.id (required).

    Relationships:
        author: The Author instance associated with this book.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    author = db.relationship("Author", back_populates="books")

    def __repr__(self) -> str:
        """Return a debug-friendly representation (useful in logs and the Python shell)."""
        return (
            f"Book(title={self.title!r}, id={self.id}, isbn={self.isbn!r}, "
            f"author_id={self.author_id}, publication_year={self.publication_year})"
        )

    def __str__(self) -> str:
        """Return a human-friendly string representation (useful for UI output)."""
        return self.title
