from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticket_booking.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer, nullable=True, default=1)
    cancellation_count = db.Column(db.Integer, nullable=False, default=0)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def update_priority(self):
        # Exponential decrease in priority after more than 5 cancellations
        self.priority = max(1, int(self.priority * 0.9))
        db.session.commit()

    def total_tickets_booked(self):
        # Calculate the total quantity of tickets booked by the user (including cancelled bookings)
        return Booking.query.filter_by(user_id=self.id).with_entities(db.func.sum(Booking.quantity)).scalar() or 0

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_cancelled = db.Column(db.Boolean, default=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    remaining_tickets = calculate_remaining_tickets()
    users_info = get_users_info()
    return render_template('index.html', remaining_tickets=remaining_tickets, users_info=users_info)

@app.route('/book', methods=['POST'])
def book_ticket():
    user_name = request.form.get('name')
    quantity = int(request.form.get('quantity'))
    
    # Check if the quantity is within the allowed limit (1 to 5)
    if not (1 <= quantity <= 5):
        return render_template('index.html', remaining_tickets=calculate_remaining_tickets(), users_info=get_users_info(), book_message='Invalid quantity. You can book 1 to 5 tickets at a time.'), 400

    user = User.query.filter_by(name=user_name).first()
    
    if not user:
        user = User(name=user_name)
        db.session.add(user)
    
    # Check the total quantity of tickets booked by the user
    total_tickets_booked = user.total_tickets_booked()
    
    # Check if the user is attempting to exceed the maximum limit of 5 tickets
    if total_tickets_booked + quantity > 5:
        return render_template('index.html', remaining_tickets=calculate_remaining_tickets(), users_info=get_users_info(), book_message='You cannot hold more than 5 tickets at any instance.'), 400

    # Check the total available tickets
    total_available_tickets = 100
    remaining_tickets = calculate_remaining_tickets()
    
    if remaining_tickets < quantity:
        return render_template('index.html', remaining_tickets=remaining_tickets, users_info=get_users_info(), book_message=f'Not enough tickets available. Remaining tickets: {remaining_tickets}'), 400
    
    # Create a new booking for the user
    new_booking = Booking(user_id=user.id, quantity=quantity)
    db.session.add(new_booking)
    
    db.session.commit()

    return render_template('index.html', remaining_tickets=remaining_tickets, users_info=get_users_info(), book_message=f'Booking for user {user.name} successful. Remaining tickets: {remaining_tickets - quantity}')

@app.route('/cancel', methods=['POST'])
def cancel_booking():
    user_name = request.form.get('name')
    quantity = int(request.form.get('quantity'))

    # Check if the quantity is within the allowed limit (1 to 5)
    if not (1 <= quantity <= 5):
        return render_template('index.html', remaining_tickets=calculate_remaining_tickets(), users_info=get_users_info(), cancel_message='Invalid quantity. You can cancel 1 to 5 tickets at a time.'), 400

    user = User.query.filter_by(name=user_name).first()

    if user:
        # Find the most recent active bookings for the user and cancel them
        recent_bookings = Booking.query.filter_by(user_id=user.id, is_cancelled=False).order_by(Booking.timestamp.desc()).limit(quantity).all()

        if recent_bookings:
            for booking in recent_bookings:
                booking.is_cancelled = True
            user.cancellation_count += quantity
            db.session.commit()

            # Update priority if more than 5 cancellations
            if user.cancellation_count > 5:
                user.update_priority()

            return render_template('index.html', remaining_tickets=calculate_remaining_tickets(), users_info=get_users_info(), cancel_message=f'{quantity} booking(s) for user {user.name} cancelled successfully.')
        else:
            return render_template('index.html', remaining_tickets=calculate_remaining_tickets(), users_info=get_users_info(), cancel_message=f'No active bookings found for user {user.name}.')
    else:
        return render_template('index.html', remaining_tickets=calculate_remaining_tickets(), users_info=get_users_info(), cancel_message='User not found.')

def get_users_info():
    users_info = []
    users = User.query.all()
    
    for user in users:
        bookings = Booking.query.filter_by(user_id=user.id).count()
        cancellations = Booking.query.filter_by(user_id=user.id, is_cancelled=True).count()
        users_info.append({'name': user.name, 'bookings': bookings, 'cancellations': cancellations, 'priority': user.priority})
    
    return users_info

def calculate_remaining_tickets():
    # Calculate the remaining available tickets
    total_available_tickets = 100
    total_booked_tickets = Booking.query.filter_by(is_cancelled=False).with_entities(db.func.sum(Booking.quantity)).scalar() or 0
    return total_available_tickets - total_booked_tickets

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
