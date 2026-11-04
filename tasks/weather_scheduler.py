
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from models import Field
from services.weather_service import (
    fetch_weather_for_location,
    store_weather_reading
)
from services.soil_service import (
    get_soil_readings_last_7_days,
    check_sensor_connection
)

logger = logging.getLogger(__name__)


def update_weather_for_all_fields(app):
    with app.app_context():
        fields = Field.query.all()

        if not fields:
            logger.info("No farm fields found.")
            return

        for field in fields:
            try:
                weather = fetch_weather_for_location(field.location)

                if not weather:
                    logger.warning(
                        f"Weather unavailable for {field.location}"
                    )
                    continue

                saved = store_weather_reading(
                    field.id,
                    weather["temperature"],
                    weather["rain"],
                    weather["humidity"]
                )

                if saved:
                    logger.info(
                        f"Weather saved for {field.location}"
                    )
                else:
                    logger.error(
                        f"Weather save failed for {field.location}"
                    )

            except Exception:
                logger.exception(
                    f"Error updating weather for {field.location}"
                )


def refresh_soil_readings(app):
    """
    Daily task to check soil readings for all farm fields.
    Runs every day at 6:00 AM.
    """
    with app.app_context():
        try:
            fields = Field.query.all()

            if not fields:
                logger.info("No farm fields found for soil checking.")
                return

            for field in fields:
                try:
                    readings = get_soil_readings_last_7_days(field.id)

                    timestamp = datetime.now().isoformat()

                    if readings:
                        logger.info(
                            f"[{timestamp}] Field {field.id} "
                            f"({field.location}): Found {len(readings)} "
                            "soil readings in the last 7 days."
                        )
                    else:
                        logger.warning(
                            f"[{timestamp}] Field {field.id} "
                            f"({field.location}): No soil readings "
                            "available in the last 7 days."
                        )

                    if not check_sensor_connection(field.id):
                        logger.warning(
                            f"Field {field.id} ({field.location}): "
                            "No soil reading in the last 24 hours."
                        )

                except Exception:
                    logger.exception(
                        f"Error checking soil readings for "
                        f"{field.location}"
                    )

            logger.info("Daily soil reading check completed.")

        except Exception:
            logger.exception("Error during daily soil reading check.")


def start_weather_scheduler(app):
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Update weather every hour
    scheduler.add_job(
        func=update_weather_for_all_fields,
        trigger="interval",
        hours=1,
        args=[app],
        id="weather_update_job",
        replace_existing=True,
        next_run_time=datetime.now()
    )

    # Check soil readings every day at 6:00 AM
    scheduler.add_job(
        func=refresh_soil_readings,
        trigger="cron",
        hour=6,
        minute=0,
        args=[app],
        id="soil_reading_refresh_job",
        replace_existing=True
    )

    scheduler.start()

    logger.info("Weather scheduler started.")
    logger.info("Daily soil reading scheduler started for 6:00 AM.")

    return scheduler
