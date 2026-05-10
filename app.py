from flask import Flask, render_template, redirect, url_for, request, session
from models import db, User, Trip, Stop, Activity, ChecklistItem, Note
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'traveloop123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traveloop.db'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Wrong email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template('signup.html', error='Email already exists!')
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', trips=trips)

@app.route('/create-trip', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        trip = Trip(
            user_id=session['user_id'],
            name=request.form['name'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            description=request.form['description']
        )
        db.session.add(trip)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_trip.html')

@app.route('/my-trips')
def my_trips():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_trips.html', trips=trips)

@app.route('/budget')
def budget():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('budget.html')

# ─── ITINERARY ROUTES ─────────────────────────────────────────────────────────

@app.route('/itinerary')
def itinerary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Get all trips for this user
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    # Show first trip by default
    selected_trip = trips[0] if trips else None
    return render_template('itinerary.html',
                           trips=trips,
                           trip=selected_trip,
                           user_name=session.get('user_name'))

@app.route('/itinerary/<int:trip_id>')
def itinerary_trip(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first()
    if not trip:
        return redirect(url_for('itinerary'))
    return render_template('itinerary.html',
                           trips=trips,
                           trip=trip,
                           user_name=session.get('user_name'))

@app.route('/itinerary/<int:trip_id>/add-stop', methods=['POST'])
def add_stop(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    stop = Stop(
        trip_id=trip_id,
        city=request.form['city'],
        arrive_date=request.form['arrive_date'],
        leave_date=request.form['leave_date']
    )
    db.session.add(stop)
    db.session.commit()
    return redirect(url_for('itinerary_trip', trip_id=trip_id))

@app.route('/itinerary/<int:trip_id>/add-activity/<int:stop_id>', methods=['POST'])
def add_activity(trip_id, stop_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    activity = Activity(
        stop_id=stop_id,
        name=request.form['name'],
        cost=float(request.form.get('cost', 0)),
        category=request.form.get('category', 'activity')
    )
    db.session.add(activity)
    db.session.commit()
    return redirect(url_for('itinerary_trip', trip_id=trip_id))

@app.route('/itinerary/<int:trip_id>/checklist/toggle/<int:item_id>')
def toggle_checklist(trip_id, item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = ChecklistItem.query.get(item_id)
    if item:
        item.is_packed = not item.is_packed
        db.session.commit()
    return redirect(url_for('itinerary_trip', trip_id=trip_id))

@app.route('/itinerary/<int:trip_id>/checklist/add', methods=['POST'])
def add_checklist(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = ChecklistItem(
        trip_id=trip_id,
        name=request.form['name'],
        is_packed=False
    )
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('itinerary_trip', trip_id=trip_id))

# ─── LOGOUT ───────────────────────────────────────────────────────────────────

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
