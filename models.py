
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float
db = SQLAlchemy()


class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )
    planting_date = db.Column(db.Date)
    variety = db.Column(db.String(255))

class Field(db.Model):
    __tablename__ = "fields"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )
    location = db.Column(db.String(255))


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    message = db.Column(db.String(255))
    sent_at = db.Column(db.DateTime)
    field_id = db.Column(db.Integer, db.ForeignKey("fields.id"), nullable=False)


class Threshold(db.Model):
    __tablename__ = "thresholds"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    temperature_min = db.Column(db.Integer)
    humidity_min = db.Column(db.Integer)
    soil_ph_min = db.Column(db.Integer)
    soil_moisture_min = db.Column(db.Integer)
    temperature_max = db.Column(db.Integer)
    humidity_max = db.Column(db.Integer)
    soil_ph_max = db.Column(db.Integer)
    soil_moisture_max = db.Column(db.Integer)


class WeatherReading(db.Model):
    __tablename__ = "weather_readings"

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey("fields.id"), nullable=False)
    temperature = db.Column(db.Integer)
    rain = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    recorded_at = db.Column(db.DateTime)


class SoilReading(db.Model):
    __tablename__ = "soil_readings"

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey("fields.id"), nullable=False)
    moisture = db.Column(db.Integer)
    ph = db.Column(Float)
    nutrients = db.Column(db.String(255))
    recorded_at = db.Column(db.DateTime)


class DiseaseRisk(db.Model):
    __tablename__ = "disease_risks"

    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=False)
    risk_score = db.Column(db.Integer)
    calculated_at = db.Column(db.DateTime)


class Observation(db.Model):
    __tablename__ = "observations"

    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=False)
    symptoms = db.Column(db.Text)
    predicted_disease = db.Column(db.String(255))
    observed_at = db.Column(db.DateTime)


class DataSource(db.Model):
    __tablename__ = "data_sources"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    source_type = db.Column(db.String(255))
    name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    configured_at = db.Column(db.DateTime)
