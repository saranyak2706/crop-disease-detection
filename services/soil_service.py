
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from models import SoilReading


def get_latest_soil_reading(field_id):
    """
    Fetch the latest soil reading for a specific field.
    """

    try:
        reading = (
            SoilReading.query
            .filter_by(field_id=field_id)
            .order_by(SoilReading.recorded_at.desc())
            .first()
        )

        return reading

    except SQLAlchemyError as e:
        print(f"Error fetching latest soil reading: {e}")
        return None


def get_soil_readings_last_7_days(field_id):
    """
    Fetch soil readings from the last 7 days.
    """

    try:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        readings = (
            SoilReading.query
            .filter(
                SoilReading.field_id == field_id,
                SoilReading.recorded_at >= seven_days_ago
            )
            .order_by(SoilReading.recorded_at.desc())
            .all()
        )

        return readings

    except SQLAlchemyError as e:
        print(f"Error fetching soil history: {e}")
        return []


def check_sensor_connection(field_id):
    """
    Check whether a field has a soil reading
    within the last 24 hours.
    """

    try:
        one_day_ago = datetime.utcnow() - timedelta(hours=24)

        recent_reading = (
            SoilReading.query
            .filter(
                SoilReading.field_id == field_id,
                SoilReading.recorded_at >= one_day_ago
            )
            .first()
        )

        return recent_reading is not None

    except SQLAlchemyError as e:
        print(f"Error checking soil sensor: {e}")
        return False


def get_sensor_status_message(field_id):
    """
    Return a friendly message about the latest soil reading.
    This checks database readings, not the physical sensor connection.
    """
    latest = get_latest_soil_reading(field_id)

    if not latest:
        return "No soil readings available. Please add a soil reading."

    if not check_sensor_connection(field_id):
        return (
            "No recent soil reading available in the last 24 hours. "
            "Please check your soil monitoring setup."
        )

    if not latest.recorded_at:
        return "Soil reading available. Update time is unknown."

    time_ago = datetime.utcnow() - latest.recorded_at
    hours_ago = int(time_ago.total_seconds() / 3600)

    if hours_ago == 0:
        return "Soil data updated just now."
    elif hours_ago == 1:
        return "Soil data updated 1 hour ago."
    else:
        return f"Soil data updated {hours_ago} hours ago."
