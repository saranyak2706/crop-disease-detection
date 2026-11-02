
from datetime import datetime
from models import db, Crop
from sqlalchemy.exc import SQLAlchemyError


def add_crop(farmer_id, name, variety, planting_date):
    """
    Add a new crop for a farmer.
    Returns: (success, message, crop_id)
    """
    try:
        # Validate planting date
        if planting_date > datetime.now().date():
            return False, "Planting date cannot be in the future.", None

        # Create crop record
        new_crop = Crop(
            farmer_id=farmer_id,
            name=name,
            variety=variety,
            planting_date=planting_date
        )

        db.session.add(new_crop)
        db.session.commit()

        return True, f"Crop '{name}' added successfully.", new_crop.id

    except SQLAlchemyError:
        db.session.rollback()
        return False, "Database error. Please try again.", None

    except Exception as e:
        db.session.rollback()
        return False, f"An error occurred: {str(e)}", None


def update_crop(crop_id, farmer_id, name, variety, planting_date):
    """
    Update an existing crop.
    Returns: (success, message)
    """
    try:
        if planting_date > datetime.now().date():
            return False, "Planting date cannot be in the future."

        # Check crop ownership
        crop = Crop.query.filter_by(
            id=crop_id,
            farmer_id=farmer_id
        ).first()

        if not crop:
            return False, "Crop not found or you don't have permission to edit it."

        crop.name = name
        crop.variety = variety
        crop.planting_date = planting_date

        db.session.commit()

        return True, f"Crop '{name}' updated successfully."

    except SQLAlchemyError:
        db.session.rollback()
        return False, "Database error. Please try again."

    except Exception as e:
        db.session.rollback()
        return False, f"An error occurred: {str(e)}"


def get_farmer_crops(farmer_id):
    """
    Fetch all crops belonging to a farmer.
    Returns: list of crop records
    """
    try:
        return Crop.query.filter_by(farmer_id=farmer_id).all()

    except SQLAlchemyError:
        return []

    except Exception:
        return []


def get_crop_by_id(crop_id, farmer_id):
    """
    Fetch a single crop and verify ownership.
    Returns: crop record or None
    """
    try:
        return Crop.query.filter_by(
            id=crop_id,
            farmer_id=farmer_id
        ).first()

    except SQLAlchemyError:
        return None

    except Exception:
        return None

def delete_crop(crop_id, farmer_id):
    try:
        crop = Crop.query.filter_by(
            id=crop_id,
            farmer_id=farmer_id
        ).first()

        if not crop:
            return False, "Crop not found or you don't have permission to delete it."

        db.session.delete(crop)
        db.session.commit()

        return True, "Crop deleted successfully."

    except SQLAlchemyError:
        db.session.rollback()
        return False, "Database error. Please try again."

    except Exception as e:
        db.session.rollback()
        return False, f"An error occurred: {str(e)}"