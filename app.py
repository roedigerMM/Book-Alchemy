from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)

#Create the tables defined in data_models.py, Only run when tables are not created yet. Comment out otherwise!
#with app.app_context():
#  db.create_all()

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    success_message = None
    error_message = None

    if request.method == 'POST':
        name = request.form.get("name")
        birth_date = request.form.get("birth_date")   # matches HTML
        date_of_death = request.form.get("date_of_death")

        if not name or not birth_date:
            error_message = "Name and birth date are required."
        else:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

            if date_of_death:
                date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d").date()
            else:
                date_of_death = None

            new_author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )

            db.session.add(new_author)
            db.session.commit()

            success_message = "Author added successfully!"

    return render_template(
        'add_author.html',
        success_message=success_message,
        error_message=error_message
    )


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    success_message = None
    error_message = None

    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get("title")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")
        isbn = request.form.get("isbn")

        if not title or not publication_year or not author_id or not isbn:
            error_message = "Title, publication year, ISBN and author id are required."
        else:
            new_book = Book(
            title = title,
            isbn = isbn,
            publication_year = int(publication_year),
            author_id = int(author_id)
            )

            db.session.add(new_book)
            db.session.commit()
            success_message = "Book added successfully!"

    return render_template(
        'add_book.html',
        authors=authors,
        success_message=success_message,
        error_message=error_message
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)