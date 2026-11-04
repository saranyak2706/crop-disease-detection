
import json
from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from sqlalchemy.exc import SQLAlchemyError
from services.soil_service import get_soil_readings_last_7_days
from models import Field, SoilReading, db
from services.soil_service import (
    get_latest_soil_reading,
    check_sensor_connection
)


soil_bp = Blueprint(
    'soil',
    __name__,
    url_prefix='/api/soil'
)


@soil_bp.route('/field/<int:field_id>', methods=['GET'])
def get_soil_data(field_id):

    print("\n========== SOIL API DEBUG ==========")
    print("Requested Field ID:", field_id)
    print("Session Farmer ID:", session.get('farmer_id'))

    # 1. Check farmer login
    farmer_id = session.get('farmer_id')

    if farmer_id is None:
        print("ERROR: Farmer is not logged in.")

        return jsonify({
            "status": "unauthorized",
            "message": "Please login first."
        }), 401

    try:
        # 2. Print database fields for debugging
        all_fields = Field.query.all()

        for f in all_fields:
            print(
                "Database Field:",
                f.id,
                "Farmer:",
                f.farmer_id,
                "Location:",
                f.location
            )

        # 3. Verify field belongs to logged-in farmer
        field = Field.query.filter_by(
            id=field_id,
            farmer_id=farmer_id
        ).first()

        if not field:
            print("ERROR: Field not found for this farmer.")

            return jsonify({
                "field_id": field_id,
                "farmer_id": farmer_id,
                "status": "not_found",
                "message": "Farm location not found for this logged-in farmer."
            }), 404

        print("Matched Field:", field.location)

        # 4. Check recent soil reading
        is_connected = check_sensor_connection(field_id)

        if not is_connected:
            print("No soil reading found in the last 24 hours.")

            return jsonify({
                "field_id": field_id,
                "location": field.location,
                "status": "disconnected",
                "message": "No soil reading received in the last 24 hours.",
                "data": None
            }), 200

        # 5. Fetch latest soil reading
        reading = get_latest_soil_reading(field_id)

        if not reading:
            return jsonify({
                "field_id": field_id,
                "status": "no_data",
                "message": "No soil data available yet.",
                "data": None
            }), 200

        # 6. Convert NPK JSON string into dictionary
        try:
            nutrients = (
                json.loads(reading.nutrients)
                if reading.nutrients
                else {}
            )

            if not isinstance(nutrients, dict):
                nutrients = {}

        except (json.JSONDecodeError, TypeError):
            nutrients = {}

        # 7. Return soil data
        response = {
            "field_id": field_id,
            "location": field.location,
            "status": "success",
            "data": {
                "moisture": reading.moisture,
                "ph": reading.ph,
                "nitrogen": nutrients.get("nitrogen"),
                "phosphorus": nutrients.get("phosphorus"),
                "potassium": nutrients.get("potassium"),
                "recorded_at": (
                    reading.recorded_at.isoformat()
                    if reading.recorded_at
                    else None
                )
            }
        }

        print("SUCCESS: Soil data fetched.")
        print("===================================\n")

        return jsonify(response), 200

    except SQLAlchemyError as e:
        print("DATABASE ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": "Database error while fetching soil data."
        }), 500

    except Exception as e:
        print("UNEXPECTED ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": "Unexpected error while fetching soil data."
        }), 500


@soil_bp.route(
    '/add-reading/<int:field_id>',
    methods=['GET', 'POST']
)
def add_soil_reading(field_id):

    # Check farmer login
    farmer_id = session.get('farmer_id')

    if farmer_id is None:
        return redirect(url_for('auth.login'))

    # Verify that this field belongs to logged-in farmer
    field = Field.query.filter_by(
        id=field_id,
        farmer_id=farmer_id
    ).first()

    if not field:
        flash("Farm location not found.", "error")
        return redirect(url_for('dashboard'))

    # Display soil entry form
    if request.method == 'GET':
        return render_template(
            'add_soil_reading.html',
            field=field
        )

    # Receive form values
    try:
        moisture = float(request.form.get('moisture'))
        ph = float(request.form.get('ph'))
        nitrogen = float(request.form.get('nitrogen'))
        phosphorus = float(request.form.get('phosphorus'))
        potassium = float(request.form.get('potassium'))

        # Validate values
        if not 0 <= moisture <= 100:
            raise ValueError("Moisture must be between 0 and 100.")

        if not 0 <= ph <= 14:
            raise ValueError("pH must be between 0 and 14.")

        if min(nitrogen, phosphorus, potassium) < 0:
            raise ValueError("NPK values cannot be negative.")

        # Store NPK values as JSON string
        nutrients = json.dumps({
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium
        })

        # Create soil reading
        reading = SoilReading(
            field_id=field.id,
            moisture=moisture,
            ph=ph,
            nutrients=nutrients,
            recorded_at=datetime.utcnow()
        )

        db.session.add(reading)
        db.session.commit()

        flash(
            f"Soil reading saved successfully for {field.location}.",
            "success"
        )

    except (ValueError, TypeError) as e:
        db.session.rollback()
        flash(f"Invalid soil data: {e}", "error")

        return redirect(
            url_for('soil.add_soil_reading', field_id=field.id)
        )

    except SQLAlchemyError:
        db.session.rollback()
        flash("Database error. Soil reading could not be saved.", "error")

        return redirect(
            url_for('soil.add_soil_reading', field_id=field.id)
        )

    return redirect(
        url_for('dashboard', field_id=field.id)
    )
@soil_bp.route('/history/<int:field_id>', methods=['GET'])
def soil_history(field_id):

    farmer_id = session.get('farmer_id')

    if farmer_id is None:
        return redirect(url_for('auth.login'))

    # Verify that this field belongs to the logged-in farmer
    field = Field.query.filter_by(
        id=field_id,
        farmer_id=farmer_id
    ).first()

    if not field:
        flash("Farm location not found.", "error")
        return redirect(url_for('dashboard'))

    # Fetch soil readings from the last 7 days
    readings = get_soil_readings_last_7_days(field_id)

    return render_template(
        'soil_history.html',
        field=field,
        readings=readings
    )