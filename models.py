from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    trips = db.relationship('Trip', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    stops = db.relationship('Stop', backref='trip', lazy=True)
    checklist = db.relationship('ChecklistItem', backref='trip', lazy=True)
    notes = db.relationship('Note', backref='trip', lazy=True)

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    city = db.Column(db.String(100))
    arrive_date = db.Column(db.String(20))
    leave_date = db.Column(db.String(20))
    activities = db.relationship('Activity', backref='stop', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stop.id'), nullable=False)
    name = db.Column(db.String(200))
    cost = db.Column(db.Float, default=0)
    category = db.Column(db.String(50))  # transport, stay, food, activity

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(200))
    is_packed = db.Column(db.Boolean, default=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    content = db.Column(db.Text)