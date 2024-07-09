from flask import Flask, render_template, appcontext_pushed, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
from random import randint

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'flightbooking123' 


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False, unique = True)

    #relationship between users and bookings
    booking = db.relationship('bookings', backref='user', lazy=True)

    def __repr__(self):
        return '<user %r>' % self.id


class flights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.Integer, nullable = False, unique=True)
    orgin = db.Column(db.VARCHAR(200), nullable = False)
    destination = db.Column(db.VARCHAR(200), nullable = False)
    departure_time = db.Column(db.DateTime, nullable = False)
    arrival_time = db.Column(db.DateTime, nullable = False)
    total_seats = db.Column(db.Integer, nullable = False, default=60)

    #relationship between users and bookings
    bookings = db.relationship('bookings', backref='flight', lazy=True)

    def __repr__(self):
        return '<Flight %r>' % self.id
    

class bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    flight_number = db.Column(db.Integer, db.ForeignKey('flights.flight_number'), nullable = False)

    def __repr__(self):
        return '<booking %r>' % self.id



class admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(200), nullable=False)
    admin_password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<admin %r>' % self.id



def add_user(getName, getEmail, getPassword):
    try:
        new_user = users(name=getName, email=getEmail, password = getPassword)
        db.session.add(new_user)
        db.session.commit()
        print("User added")
        return True

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)
        return False

def add_flights(getFlightNumber, getOrigin, getDestination, getDepartureTIme, getArrivalTime, getTotalSeats):
    try:

        new_flight = flights(
            flight_number=getFlightNumber,
            orgin=getOrigin,
            destination=getDestination,
            departure_time=getDepartureTIme,
            arrival_time=getArrivalTime,
            total_seats=getTotalSeats,
           
            )

        db.session.add(new_flight);
        db.session.commit()
        return new_flight

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)
        return False

def remove_flights(getFlightNumber):
    try:
        flight = flights.query.filter_by(flight_number=getFlightNumber).first()
        
        # Check if flight exists
        if flight:
            db.session.delete(flight)
            db.session.commit()
            print("Flight deleted successfully.")
        else:
            print("Flight not found.")
       

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)


def add_bookings(getUserId, getFlightNumber):
    try:
        new_booking = bookings(user_id = getUserId, flight_number = getFlightNumber)

        db.session.add(new_booking);
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)
        return False

def authenticate(getEmail, getPassword):
    try:
        
        user = users.query.filter_by(email=getEmail).first()
        print("user",user.password)
        print("password", getPassword)
        # Check if user exists
        if user and user.password == getPassword:
            return user
        else:
            print("Ia m flase")
            return False
       

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)
    

def admin_authenticate(getAdminEmail, getAdminPassword):
    try:
        admin_user = admin.query.filter_by(admin_email=getAdminEmail).first()
        
        # Check if user exists
        if admin_user and admin_user.admin_password == getAdminPassword:
            return admin
        else:
            return False
       

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)


def query(getQuery, params):
    try:

        with db.engine.connect() as connection:
            result = connection.execute(text(getQuery), params)
            rows = [dict(row) for row in result.mappings()]  # Convert rows to dictionaries
        return rows

    except Exception as e:
        db.session.rollback()
        print("Error occurred:", e)
        return False;



    

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        login_email = request.form['email']  
        password = request.form['password']

        user = authenticate(login_email, password) 

        print(login_email)
        print(password)

        if(user):
            user_db = query("select * from users where email = :email", {'email' :login_email})
            session['user_id'] = user_db[0]['id']
            print(session['user_id'])
            print("Login success")
            return redirect('/home')  

        else:
            print("Login unsuccessfull")
            return render_template("login.html", message = "login unsuccessfull")
        
    else:
        return render_template("login.html", message = "Enter the credentials asap")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    print('You have been logged out.', 'success')
    return redirect('/login')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if(request.method == 'POST'):
        name = request.form['name']
        email = request.form['email']  
        password = request.form['password']

        user = authenticate(email, password)  

        if(user):
            print("User already exists try login in")
            return render_template("signup.html", message ="User already exists try login in" )

        else:
            isUserAddSuccess = add_user(name, email, password)

            if(isUserAddSuccess):
                return redirect('/home')

            else:
                return render_template("signup.html", message ="Some error occured Sign up again" )

        
    else:
        return render_template("signup.html")



@app.route('/')
def userType():
    return render_template('user.html')


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        admin_email = request.form['email']
        admin_password = request.form['password']

        admin = admin_authenticate(admin_email, admin_password)

        if(admin):
            print(admin)
            session['admin_id'] = randint(0,1000000000) 
            result = query("SELECT * FROM flights;", None)
            session['flight_info_table'] = result
            return redirect('/admincontrol')

        else:
            return  render_template('adminlogin.html', message = "Invalid credential try again")
    else:
        return render_template('adminlogin.html', message = "fill details asap")


@app.route('/admincontrol')
def admincontrol():
    if 'admin_id' not in session:
        print('You need to log in as admin first.', 'danger')
        return redirect('/adminlogin')

    flight_info_table = session.pop('flight_info_table', None)  # Retrieve and remove the data from the session
    if flight_info_table is None:
        flight_info_table = query("SELECT * FROM flights", None)
    return render_template('adminControl.html', flight_info_table=flight_info_table)


@app.route('/search', methods= ['GET', 'POST'])
def search():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        flightNumber = request.form['flight_number']

        dt_str = date +' ' +time+':00'
        dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        dt_result = dt_str + '.000000'
        print(dt_result)

        result = query("SELECT * FROM flights WHERE flight_number = :flight_number OR arrival_time = :arrival_time",
        {'flight_number': flightNumber, 'arrival_time': dt_result})

        if(result):
            print(result)
            session['flight_info_table'] = result
            return redirect('/admincontrol')
        else:
            print("Something went wrong")
            return redirect('/search')

    else:
        session.pop('flight_info_table', None)
        # all_flight_data = query("SELECT * FROM flights", None)
        # flight_info_table = session.get('flight_info_table', [])
        # return render_template("adminControl.html", flight_info_table = flight_info_table)


@app.route('/flight_search', methods= ['GET', 'POST'])
def flight_search():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        flightNumber = request.form['flight_number']

        dt_str = date +' ' +time+':00'
        dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        dt_result = dt_str + '.000000'
        print(dt_result)

        result = query("SELECT * FROM flights WHERE flight_number = :flight_number OR arrival_time = :arrival_time",
        {'flight_number': flightNumber, 'arrival_time': dt_result})

        if(result):
            print(result)
            session['flight_info_table'] = result
            return redirect('/home')
        else:
            print("Something went wrong")
            return redirect('/flight_search')

    else:
        session.pop('flight_info_table', None)
        all_flight_data = query("SELECT * FROM flights", None)
        flight_info_table = session.get('flight_info_table', [])
        return render_template("home.html", flight_info_table = flight_info_table)

@app.route('/addflights', methods= ['GET', 'POST'])
def addflights():
    if(request.method == 'POST'):
        flightnumber = request.form['flightnumber']
        origin = request.form['origin']
        destination = request.form['destination']
        arrival_time = request.form['arrival_time']
        departure_time = request.form['departure_time']
        date = request.form['date']
        seats = request.form['seats']

        dt_str_arrival = date +' ' +arrival_time+':00'
        dt_obj_arrival = datetime.strptime(dt_str_arrival, "%Y-%m-%d %H:%M:%S")

        dt_str_departure = date +' ' +departure_time+':00'
        dt_obj_departure = datetime.strptime(dt_str_departure, "%Y-%m-%d %H:%M:%S")

        flight_add = add_flights(flightnumber, origin, destination, dt_obj_departure, dt_obj_arrival, seats)

        flights_details = query("select * from flights", None)

        if(flight_add):
            print("Flight added successfully")
            result = query("SELECT * FROM flights;", None)
            session['flight_info_table'] = result
            return redirect('/admincontrol')

        else:
            print("There was an error try again")
            return redirect('/admincontrol')

    else:
        return render_template("adminControl.html")


@app.route('/removeflight', methods= ['GET', 'POST'])
def removeflight():
    if(request.method == 'POST'):
        flight_number = request.form['flight_number']
        
    try:
        flight = flights.query.filter_by(flight_number=flight_number).first()
        booking = bookings.query.filter_by(flight_number=flight_number).first()
        # Check if flight exists
        if flight:
            db.session.delete(flight)
            db.session.delete(booking)
            db.session.commit()
            print(f"Flight number {flight_number} deleted successfully.")
            return redirect('/admincontrol')
        else:
            print(f"Flight number {flight_number} not found.")
            return redirect('/admincontrol')
       
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")
        return redirect('/admincontrol')



@app.route('/home')
def home():
    if 'user_id' not in session:
        print('You need to log in first.', 'danger')
        return redirect('/login')

    flight_info_table = session.pop('flight_info_table', None)  # Retrieve and remove the data from the session
    if flight_info_table is None:
        flight_info_table = query("SELECT * FROM flights", None)
    return render_template('home.html', flight_info_table=flight_info_table)

@app.route('/bookTicket', methods = ['GET', 'POST'])
def booktickets():
    if(request.method == 'POST'):
        flight_number = request.form['flight_number']
        isBooking = add_bookings(session['user_id'], flight_number)

        if(isBooking):
            print(query("Select * from bookings", None))
            return redirect('/home')

        else:
            print("Something went wrong")
            return redirect('/home')


@app.route('/mybookings', methods = ['GET', 'POST'])
def mybookings():
    if(request.method == 'POST'):
        user_id = session['user_id']
        flight_details  = query("SELECT f.* FROM flights f JOIN bookings b ON f.flight_number = b.flight_number WHERE b.user_id = :user_id;",
         {'user_id' : user_id})

        session['flight_info_table'] =  flight_details
        print(flight_details)
        return redirect('/home')
        
    

if __name__ == "__main__":
    app.run(debug = True)