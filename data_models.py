from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    """
    Represents an author in the library system.

    Attributes:
        id (int): Primary key, unique identifier for the author.
        name (str): Full name of the author.
        birth_date (date): The author's date of birth.
        date_of_death (date or None): The author's date of death, if applicable.

    Relationships:
        books (list of Book): One-to-many relationship to the books written by the author.
    """
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        """
        Returns a concise and unambiguous string representation of the Author instance,
        useful for debugging and logging.

        Returns:
            str: Debug-style string with the author's name and birth date.
        """
        return f"<Author {self.name}, born {self.birth_date}>"

    def __str__(self):
        """
        Returns a readable string representation of the Author instance.

        Returns:
            str: Human-readable description of the author including name,
                 birth date, and (optionally) date of death.
        """
        return f"Author: {self.name}, Born: {self.birth_date}, Died: {self.date_of_death if self.date_of_death else 'N/A'}"


class Book(db.Model):
    """
    Represents a book in the library system.

    Attributes:
        id (int): Primary key, unique identifier for the book.
        isbn (str): International Standard Book Number, must be unique.
        title (str): Title of the book.
        publication_year (int): Year the book was published.
        cover_url (str or None): Optional URL to the book’s cover image.
        author_id (int): Foreign key reference to the Author.
        author (Author): SQLAlchemy relationship to the associated Author.

    Relationships:
        author (Author): Each book is linked to a single author.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    cover_url = db.Column(db.String(255), nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        """
        Returns a concise and unambiguous string representation of the Book instance,
        useful for debugging and logging.

        Returns:
            str: Debug-style string with the book’s title, author, and ISBN.
        """
        return f"<Book {self.title} by {self.author.name}, ISBN: {self.isbn}>"

    def __str__(self):
        """
        Returns a readable string representation of the Book instance.

        Returns:
            str: Human-readable description of the book including title, ISBN,
                 publication year, and the author’s name.
        """
        return f"Book: {self.title}, ISBN: {self.isbn}, Published: {self.publication_year}, Author: {self.author.name}"
