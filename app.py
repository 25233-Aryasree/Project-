from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Transaction
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'finance-security-framework-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_identity_v3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user') # For demo, we'll allow setting role or default to 'user'

        user_exists = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
        if user_exists:
            flash('Username or Email already exists.', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def user_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard_user.html', user=current_user)

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('user_dashboard'))
    
    users = User.query.all()
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('dashboard_admin.html', users=users, transactions=transactions)

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    
    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'User {user_to_delete.username} deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/deposit', methods=['POST'])
@login_required
def deposit():
    amount = float(request.form.get('amount', 0))
    if amount > 0:
        current_user.balance += amount
        transaction = Transaction(user_id=current_user.id, type='Deposit', amount=amount)
        db.session.add(transaction)
        db.session.commit()
        flash(f'Successfully deposited ${amount:,.2f}.', 'success')
    else:
        flash('Invalid deposit amount.', 'error')
    return redirect(url_for('user_dashboard'))

@app.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    amount = float(request.form.get('amount', 0))
    if 0 < amount <= current_user.balance:
        current_user.balance -= amount
        transaction = Transaction(user_id=current_user.id, type='Withdraw', amount=amount)
        db.session.add(transaction)
        db.session.commit()
        flash(f'Successfully withdrew ${amount:,.2f}.', 'success')
    elif amount > current_user.balance:
        flash('Insufficient funds for this withdrawal.', 'error')
    else:
        flash('Invalid withdrawal amount.', 'error')
    return redirect(url_for('user_dashboard'))

# --- Initialization ---

def init_db():
    with app.app_context():
        db.create_all()
        # Create a default admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin_user = User(
                username='admin',
                email='admin@finance.com',
                password_hash=generate_password_hash('AdminPass123', method='scrypt'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin / AdminPass123")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
