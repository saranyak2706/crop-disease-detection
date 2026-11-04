import os
import requests
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from models import db, WeatherReading
from dotenv import load_dotenv
load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'


def fetch_weather_for_location(location):
    """
    Fetches current weather for a farm location.
    Returns a dictionary or None if fetching fails.
    """

    if not WEATHER_API_KEY:
        print("Weather API key not set in .env file.")
        return None

    params = {
        'q': location,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }

    try:
        response = requests.get(
            WEATHER_API_URL,
            params=params,
            timeout=5
        )

        response.raise_for_status()
        data = response.json()

        weather = {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'rain': data.get('rain', {}).get('1h', 0),
            'location': data['name'],
            'timestamp': datetime.utcnow()
        }

        return weather

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch weather: {e}")
        return None

    except (KeyError, ValueError) as e:
        print(f"Invalid weather API response: {e}")
        return None

def store_weather_reading(field_id, temperature, rain, humidity):
    """
    Saves weather data for a specific farm field.
    Returns True if successful, False otherwise.
    """

    try:
        weather = WeatherReading(
            field_id=field_id,
            temperature=round(temperature),
            rain=round(rain),
            humidity=round(humidity),
            recorded_at=datetime.utcnow()
        )

        db.session.add(weather)
        db.session.commit()

        return True

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error while saving weather: {e}")
        return False

    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error while saving weather: {e}")
        return False


def get_latest_weather_for_field(field_id):
    """
    Retrieves the latest weather reading for a specific field.
    Returns weather data as a dictionary or None.
    """

    try:
        weather = WeatherReading.query.filter_by(
            field_id=field_id
        ).order_by(
            WeatherReading.recorded_at.desc()
        ).first()

        if weather:
            return {
                'temperature': weather.temperature,
                'rain': weather.rain,
                'humidity': weather.humidity,
                'recorded_at': weather.recorded_at
            }

        return None

    except SQLAlchemyError as e:
        print(f"Error retrieving weather data: {e}")
        return None

def get_weather_history(field_id, limit=20):
    """
    Retrieve previous weather readings for a farm field.
    Latest readings will appear first.
    """

    try:
        records = (
            WeatherReading.query
            .filter_by(field_id=field_id)
            .order_by(WeatherReading.recorded_at.desc())
            .limit(limit)
            .all()
        )

        history = []

        for record in records:
            history.append({
                "temperature": record.temperature,
                "humidity": record.humidity,
                "rain": record.rain,
                "recorded_at": record.recorded_at
            })

        return history

    except Exception as e:
        print(f"Error fetching weather history: {e}")
        return []

def get_weather_analytics(field_id, days=7):
    """
    Calculate weather analytics for a farm field.
    Default period: Last 7 days.
    """

    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        records = (
            WeatherReading.query
            .filter(
                WeatherReading.field_id == field_id,
                WeatherReading.recorded_at >= start_date
            )
            .order_by(WeatherReading.recorded_at.asc())
            .all()
        )

        if not records:
            return None

        temperatures = [r.temperature for r in records]
        humidity_values = [r.humidity for r in records]
        rainfall_values = [r.rain for r in records]

        analytics = {
            "average_temperature": round(
                sum(temperatures) / len(temperatures), 2
            ),
            "maximum_temperature": max(temperatures),
            "minimum_temperature": min(temperatures),
            "average_humidity": round(
                sum(humidity_values) / len(humidity_values), 2
            ),
            "average_rainfall": round(
                sum(rainfall_values) / len(rainfall_values), 2
            ),
            "total_records": len(records),
            "period_days": days
        }

        return analytics

    except Exception as e:
        print(f"Error calculating weather analytics: {e}")
        return None