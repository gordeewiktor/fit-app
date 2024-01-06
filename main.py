
from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = '281deaf9b98df862ed55f39e00d437c6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitnessclub.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'client' or 'coach'

# Workout Plan Model
class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        role = request.form['role']  # Assume the form has a 'role' field to specify if the user is a client or a coach

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return "Incorrect username or password."

    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user_role = session['user_role']
        if user_role == 'coach':
            # Coaches can see all the workout plans they've assigned
            plans = WorkoutPlan.query.filter_by(coach_id=user_id).all()
        else:
            # Clients can see only their workout plans
            plans = WorkoutPlan.query.filter_by(client_id=user_id).all()
        return render_template('dashboard.html', plans=plans)
    else:
        return redirect(url_for('login'))

# Add Workout Plan route (for coaches)
@app.route('/add_plan', methods=['GET', 'POST'])
def add_plan():
    if 'user_role' in session and session['user_role'] == 'coach':
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            client_id = request.form['client_id']  # Assume the coach knows the client ID

            new_plan = WorkoutPlan(title=title, description=description, client_id=client_id)
            db.session.add(new_plan)
            db.session.commit()

            return redirect(url_for('dashboard'))
        return render_template('add_plan.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)









