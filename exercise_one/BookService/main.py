from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# Fetch environment variables
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Book Model
class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publish_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "publish_date": self.publish_date.strftime('%Y-%m-%d')  # Format the date as a string
        }

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# CREATE a book
@app.route('/books/add', methods=['POST'])
def create_book():
    data = request.json
    # Parse the publish_date from the incoming data
    publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()

    book = Book(
        book_id=data['book_id'],
        title=data['title'],
        author=data['author'],
        publish_date=publish_date
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

# READ all books
@app.route('/books/all', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# READ a single book by ID
@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id: str):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200

# UPDATE a book by book_id
@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id: str):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.json
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'publish_date' in data:
        book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(book.to_dict()), 200

# DELETE a book by book_id
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id: str):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
