from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import pika
import json
import requests
import time
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app and database setup
app = Flask(__name__)

# Load environment variables
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Borrow model
class Borrow(db.Model):
    __tablename__ = 'borrowed_books'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    book_id = db.Column(db.String(20), nullable=False)
    date_borrowed = db.Column(db.Date, nullable=False)
    date_returned = db.Column(db.Date, nullable=False) 
    def to_dict(self):
        return {
            "student_id": self.student_id,
            "book_id": self.book_id,
            "date_borrowed": self.date_borrowed.isoformat(),
            "date_returned": self.date_returned.isoformat()
        }

# Initialize the database
with app.app_context():
    db.create_all()

def check_student_exists(student_id):
    try:
        user_service_url = os.getenv("USER_SERVICE_URL")
        response = requests.get(f"{user_service_url}/{student_id}")
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Error checking student existence: {e}")
        return False

def check_book_exists(book_id):
    try:
        book_service_url = os.getenv("BOOK_SERVICE_URL")
        response = requests.get(f"{book_service_url}/{book_id}")
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Error checking book existence: {e}")
        return False

# RabbitMQ consumer function 
def consume_borrow_requests():
    while True:  
        try:
            credentials = pika.PlainCredentials(
                os.getenv("RABBITMQ_DEFAULT_USER"),
                os.getenv("RABBITMQ_DEFAULT_PASS")
            )
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                    credentials=credentials,
                    heartbeat=60000,
                    blocked_connection_timeout=300
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue='borrow_book', durable=True)

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    student_id = data['student_id']
                    book_id = data['book_id']
                    logger.info(f"Received borrow request for student {student_id} and book {book_id}")

                    # Check if the student and book exist
                    if not check_student_exists(student_id):
                        logger.error(f"Student {student_id} does not exist.")
                        return

                    if not check_book_exists(book_id):
                        logger.error(f"Book {book_id} does not exist.")
                        return

                    # Check the borrow limit
                    with app.app_context():
                        borrowed_count = Borrow.query.filter_by(student_id=student_id).count()
                        logger.info(f"Student {student_id} currently has {borrowed_count} books borrowed.")

                        if borrowed_count < 5:
                            new_borrow = Borrow(
                                student_id=student_id,
                                book_id=book_id,
                                date_borrowed=data['date_borrowed'],
                                date_returned=data['date_returned']
                            )
                            db.session.add(new_borrow)
                            db.session.commit()
                            logger.info(f"Borrow request processed for student {student_id} and book {book_id}")
                        else:
                            logger.warning(
                                f"Borrow request denied: Student {student_id} has reached the borrowing limit."
                            )
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                finally:
                    ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message after processing

            channel.basic_consume(queue='borrow_book', on_message_callback=callback, auto_ack=False)
            logger.info("Waiting for messages in RabbitMQ queue 'borrow_book'.")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection lost: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Expose an HTTP endpoint to view all borrowed books
@app.route('/borrowed_books', methods=['GET'])
def get_borrowed_books():
    try:
        borrowed_books = Borrow.query.all()
        return jsonify([borrow.to_dict() for borrow in borrowed_books]), 200
    except Exception as e:
        logger.error(f"Error fetching borrowed books: {e}")
        return jsonify({"error": "Failed to fetch borrowed books"}), 500

@app.route('/borrowed_books/clear', methods=['DELETE'])
def clear_borrowed_books():
    try:
        Borrow.query.delete()
        db.session.commit()
        return jsonify({"message": "All borrowed book records deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete borrowed book records: {str(e)}"}), 500

@app.route('/test_borrow_count/<student_id>', methods=['GET'])
def test_borrow_count(student_id):
    with app.app_context():
        borrowed_count = Borrow.query.filter_by(student_id=student_id).count()
        return jsonify({"student_id": student_id, "borrowed_count": borrowed_count}), 200

if __name__ == "__main__":
    import threading
    # Start RabbitMQ consumer in a separate thread
    consumer_thread = threading.Thread(target=consume_borrow_requests)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Start Flask app
    app.run(host="0.0.0.0", port=5003)
