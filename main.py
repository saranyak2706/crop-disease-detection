
import os
import logging
import json
from flask import (
    Flask,
    redirect,
    url_for,
    session,
    render_template,
    flash,
    request
)

from config import Config
from models import Field, db

from routes.auth import auth_bp
from routes.password_reset import reset_bp
from routes.farmer_routes import farmer_bp
from routes.soil_routes import soil_bp

from tasks.weather_scheduler import start_weather_scheduler

from screens.farm_dashboard import (
    build_weather_cards,
    get_farmer_fields,
    build_all_soil_cards
)

from services.weather_service import (
    fetch_weather_for_location,
    store_weather_reading
)


# Configure logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.config.from_object(Config)
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if value else {}
    except (ValueError, TypeError):
        return {}



# Initialize database
db.init_app(app)


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(farmer_bp)
app.register_blueprint(soil_bp)


# Create database tables
with app.app_context():
    db.create_all()


# Home route
@app.route('/')
def home():
    return redirect(url_for('auth.login'))


# Dashboard route

@app.route('/dashboard')
def dashboard():
    if 'farmer_id' not in session:
        return redirect(url_for('auth.login'))

    farmer_id = session['farmer_id']

    # Get all locations belonging to this farmer
    fields = get_farmer_fields(farmer_id)

    # Get selected location for Weather section
    selected_field_id = request.args.get(
        'field_id',
        type=int
    )

    # Default to latest location
    if not selected_field_id or not any(
        field.id == selected_field_id
        for field in fields
    ):
        selected_field_id = fields[0].id if fields else None

    # Weather: show only selected location
    weather_cards = build_weather_cards(
        farmer_id,
        selected_field_id
    )

    # Soil Health: show ALL locations of this farmer
    soil_cards = build_all_soil_cards(farmer_id)

    return render_template(
        'dashboard.html',
        weather_cards=weather_cards,
        soil_cards=soil_cards,
        fields=fields,
        selected_field_id=selected_field_id
    )

# Refresh weather route
@app.route('/refresh-weather', methods=['POST'])
def refresh_weather():

    if 'farmer_id' not in session:
        return redirect(url_for('auth.login'))

    farmer_id = session['farmer_id']

    selected_field_id = request.form.get(
        'field_id',
        type=int
    )

    # Verify selected field belongs to logged-in farmer
    field = Field.query.filter_by(
        id=selected_field_id,
        farmer_id=farmer_id
    ).first() if selected_field_id else None

    if not field:
        flash("Please select a valid farm location.", "error")
        return redirect(url_for('dashboard'))

    try:
        weather = fetch_weather_for_location(field.location)

        if weather:
            saved = store_weather_reading(
                field.id,
                weather["temperature"],
                weather["rain"],
                weather["humidity"]
            )

            if saved:
                flash(
                    f"Weather updated for {field.location}.",
                    "success"
                )
            else:
                flash(
                    "Weather data could not be saved.",
                    "error"
                )
        else:
            flash(
                f"Weather data unavailable for {field.location}.",
                "error"
            )

    except Exception as e:
        logging.exception("Weather update failed")
        flash("Weather update failed. Please try again.", "error")

    return redirect(
        url_for(
            'dashboard',
            field_id=selected_field_id
        )
    )


if __name__ == '__main__':

    debug_mode = True

    # Avoid duplicate schedulers with Flask debug reloader
    if (
        not debug_mode
        or os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    ):
        scheduler = start_weather_scheduler(app)

    app.run(debug=debug_mode)
