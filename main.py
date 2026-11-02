
from flask import Flask, redirect, url_for, session, render_template
from config import Config
from models import db, Farmer
from routes.auth import auth_bp
from routes.password_reset import reset_bp
from routes.farmer_routes import farmer_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(farmer_bp)

# Create database tables
with app.app_context():
    db.create_all()


# Home route - Redirect to login
@app.route('/')
def home():
    return redirect(url_for('auth.login'))


# Dashboard route
@app.route('/dashboard')
def dashboard():

    if 'farmer_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
