import os
import re
import logging
import requests

from flask import Flask, request, redirect, url_for, render_template, flash
from datetime import datetime
from data_models import db, Author, Book

app = Flask(__name__)

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)
app.secret_key = 'example_key'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Handles the addition of a new author to the database.

    GET: Renders a form to input new author details.
    POST: Processes the submitted form to add a new author.
        - Checks if the author already exists by name.
        - Parses and validates birth and death dates.
        - Adds the author to the database if not present.

    Flash messages are used to inform the user of success or duplication.

    Returns:
        Rendered HTML template for author input or redirect on success.
    """
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birthdate']
        date_of_death = request.form.get('date_of_death')

        today = datetime.today().date()

        if birth_date:
            birth_date = datetime.strptime(birth_date, '%m/%d/%Y').date()

            if birth_date > today:
                flash("Birth date cannot be in the future.", 'error')
                return redirect(url_for('add_author'))

        if date_of_death:
            date_of_death = datetime.strptime(date_of_death, '%m/%d/%Y').date()

            if date_of_death > today:
                flash("Death date cannot be in the future.", 'error')
                return redirect(url_for('add_author'))

            if birth_date and date_of_death < birth_date:
                flash("Death date cannot be before birth date.", 'error')
                return redirect(url_for('add_author'))

        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            flash(f"Author {name} already exists in the database.", 'error')
            return redirect(url_for('add_author'))

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        flash(f"Author {name} added successfully!", 'success')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Handles the addition of a new book to the database.

    GET:
        - Retrieves the form for adding a new book, displaying a list of available authors.
    POST:
        - Processes the submitted data (title, ISBN, publication year, and selected author).
        - Adds the new book to the database and commits the changes.

    Flash messages will notify the user whether the book was successfully added or if there were errors.

    Returns:
        - The rendered HTML form for adding a book or a redirect to the same page on success.
    """
    authors = Author.query.all()

    if request.method == 'POST':
        isbn = request.form['isbn']

        if not is_valid_isbn(isbn):
            flash("Invalid ISBN format. Please enter a valid ISBN (ISBN-13 starting with 978).",
                  'error')
            return redirect(url_for('add_book'))

        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        new_book = Book(isbn=isbn, title=title, publication_year=publication_year,
                        author_id=author_id)

        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{title}' added successfully!", 'success')
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route('/', methods=['GET'])
def home():
    """
    Displays the homepage with a list of books.

    - Supports optional search via the 'query' parameter to filter by title.
    - Supports sorting via the 'sort_by' parameter (by title or author).
    - Adds cover URLs to each book entry using the Open Library API.
    - Shows a message if no books match the search query.

    Returns:
        Rendered HTML template with the list of books, sorting, and messages.
    """
    sort_by = request.args.get('sort_by', 'title')
    search_query = request.args.get('query', '')

    if search_query:
        books_query = Book.query.filter(Book.title.ilike(f"%{search_query}%"))
    else:
        books_query = Book.query

    if sort_by == 'author':
        books = books_query.join(Author).order_by(Author.name).all()
    else:
        books = books_query.order_by(Book.title).all()

    for book in books:
        book.cover_url = get_cover_url(book.isbn)

    message = None
    if search_query and not books:
        message = "No books found matching your search."

    return render_template(
        'home.html',
        books=books,
        sort_by=sort_by,
        query=search_query,
        message=message
    )



def get_cover_url(isbn):
    """
    Retrieves the cover image URL for a given book by ISBN.

    - Checks if a cover URL is already stored in the database.
    - If not, fetches book data from the Open Library API.
    - Extracts the 'large' cover URL if available and updates the database.
    - If no cover is found, stores and returns a default placeholder image URL.

    Args:
        isbn (str): The ISBN of the book.

    Returns:
        str: The URL of the book cover image.
    """
    book = Book.query.filter_by(isbn=isbn).first()
    if book and book.cover_url:
        return book.cover_url

    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if f"ISBN:{isbn}" in data:
            book_data = data[f"ISBN:{isbn}"]
            cover_id = book_data.get("cover", {}).get("large")
            if cover_id:
                cover_url = f"{cover_id}"
                logger.debug(f"Cover URL for ISBN {isbn}: {cover_url}")

                if book:
                    book.cover_url = cover_url
                else:
                    book = Book(isbn=isbn, cover_url=cover_url)
                    db.session.add(book)

                db.session.commit()
                return cover_url

    default_cover_url = "https://via.placeholder.com/150?text=No+Cover+Available"
    if book:
        book.cover_url = default_cover_url
        db.session.commit()

    logger.warning(f"No cover found for ISBN {isbn}, using default cover.")
    return default_cover_url

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Deletes a book entry from the database.

    - Removes the book with the given ID.
    - Also deletes the associated author if they have no other books.
    - Uses flash messages to inform the user of the deletion outcome.

    Args:
        book_id (int): The unique ID of the book to delete.

    Returns:
        Redirect to the homepage after deletion.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f'Book "{book.title}" and its author "{author.name}" were deleted.', 'success')
    else:
        flash(f'Book "{book.title}" was deleted.', 'success')

    return redirect(url_for('home'))


def is_valid_isbn(isbn):
    """
    Validates the ISBN-13 format (starts with 978 and has 13 digits).

    Args:
        isbn (str): The ISBN number to validate.

    Returns:
        bool: True if the ISBN is valid, False otherwise.
    """
    isbn = isbn.replace("-", "").replace(" ", "")

    if len(isbn) == 13 and isbn.startswith("978"):
        return bool(re.match(r'^\d{13}$', isbn)) and check_isbn13(isbn)

    return False


def check_isbn13(isbn):
    """
    Validates an ISBN-13 using the checksum calculation.

    Args:
        isbn (str): The ISBN-13 number to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    total = 0
    for i in range(12):
        digit = int(isbn[i])
        if i % 2 == 0:
            total += digit
        else:
            total += digit * 3

    checksum = 10 - (total % 10)
    if checksum == 10:
        checksum = 0

    return int(isbn[12]) == checksum


# with app.app_context():
# db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
