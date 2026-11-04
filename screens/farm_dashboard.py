
import json
from datetime import datetime, timedelta

from models import Field
from services.weather_service import get_latest_weather_for_field
from services.soil_service import (
    get_latest_soil_reading,
    check_sensor_connection, get_sensor_status_message
)


def get_farmer_fields(farmer_id):
    """Return all farm locations belonging to the logged-in farmer."""
    return (
        Field.query
        .filter_by(farmer_id=farmer_id)
        .order_by(Field.id.desc())
        .all()
    )


# ---------------- WEATHER ----------------

def is_weather_stale(recorded_at):
    if not recorded_at:
        return True

    time_difference = datetime.utcnow() - recorded_at
    return time_difference > timedelta(hours=1)


def build_weather_cards(farmer_id, selected_field_id=None):
    fields = get_farmer_fields(farmer_id)

    if selected_field_id:
        fields = [
            field for field in fields
            if field.id == selected_field_id
        ]

    weather_cards = []

    for field in fields:
        weather_reading = get_latest_weather_for_field(field.id)

        if (
            not weather_reading
            or is_weather_stale(weather_reading["recorded_at"])
        ):
            weather_cards.append({
                "field_id": field.id,
                "status": "unavailable",
                "location": field.location,
                "temperature": None,
                "rain": None,
                "humidity": None,
                "recorded_at": None
            })
        else:
            weather_cards.append({
                "field_id": field.id,
                "status": "success",
                "location": field.location,
                "temperature": weather_reading["temperature"],
                "rain": weather_reading["rain"],
                "humidity": weather_reading["humidity"],
                "recorded_at": weather_reading["recorded_at"]
            })

    return weather_cards


# ---------------- SOIL HEALTH ----------------

def build_soil_health_card(field_id, location):
    try:
        reading = get_latest_soil_reading(field_id)

        if not reading:
            return {
                "field_id": field_id,
                "location": location,
                "status": "no_data",
                "message": "No soil data available yet."
            }

        is_connected = check_sensor_connection(field_id)

        if not is_connected:
            return {
                "field_id": field_id,
                "location": location,
                "status": "disconnected",
                "message": (
                    "No soil reading received in the last 24 hours."
                )
            }

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

        return {
            "field_id": field_id,
            "location": location,
            "status": "success",
            "moisture": reading.moisture,
            "ph": reading.ph,
            "nitrogen": nutrients.get("nitrogen"),
            "phosphorus": nutrients.get("phosphorus"),
            "potassium": nutrients.get("potassium"),
            "recorded_at": reading.recorded_at,
            "sensor_message": get_sensor_status_message(field_id)
        }

    except Exception as e:
        print(
            f"Soil card error for Field ID {field_id}, "
            f"Location {location}: {e}"
        )
        
        return {
            "field_id": field_id,
            "location": location,
            "status": "error",
            "message": "Could not fetch soil data."
        }


def build_all_soil_cards(farmer_id):
    """Build a separate soil card for every farm of this farmer."""
    fields = get_farmer_fields(farmer_id)

    soil_cards = []

    for field in fields:
        soil_card = build_soil_health_card(
            field.id,
            field.location
        )

        soil_cards.append(soil_card)

    return soil_cards
