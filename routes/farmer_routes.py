from flask import Blueprint, render_template, request, jsonify, session, redirect
from services.crop_service import add_crop, update_crop, get_farmer_crops,delete_crop
from models import db, Crop
from datetime import datetime

farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')
@farmer_bp.route('/my-crops', methods=['GET'])
def my_crops():
    """
    Show the My Crops page with the farmer's existing crops.
    """
    farmer_id = session.get('farmer_id')

    if not farmer_id:
        return redirect('/auth/login')

    crops = get_farmer_crops(farmer_id)

    return render_template('farmer/my_crops.html', crops=crops)

@farmer_bp.route('/save-crop', methods=['POST'])
def save_crop():
    """
    Handle adding or updating a crop.
    """
    farmer_id = session.get('farmer_id')

    if not farmer_id:
        return jsonify({
            "success": False,
            "message": "Not logged in."
        }), 401

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    crop_id = data.get('crop_id')
    name = data.get('name', '').strip()
    variety = data.get('variety', '').strip()
    planting_date_str = data.get('planting_date', '').strip()

    if not name or not variety or not planting_date_str:
        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    try:
        planting_date = datetime.strptime(
            planting_date_str, '%Y-%m-%d'
        ).date()
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid date format. Use YYYY-MM-DD."
        }), 400

    if crop_id is None:
        success, message, new_crop_id = add_crop(
            farmer_id, name, variety, planting_date
        )

        return jsonify({
            "success": success,
            "message": message,
            "crop_id": new_crop_id
        }), (200 if success else 400)

    else:
        try:
            crop_id = int(crop_id)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid crop ID."
            }), 400

        success, message = update_crop(
            crop_id, farmer_id, name, variety, planting_date
        )

        return jsonify({
            "success": success,
            "message": message,
            "crop_id": crop_id
        }), (200 if success else 400)

@farmer_bp.route('/delete-crop/<int:crop_id>', methods=['DELETE'])
def remove_crop(crop_id):
    farmer_id = session.get('farmer_id')

    if not farmer_id:
        return jsonify({
            "success": False,
            "message": "Not logged in."
        }), 401

    success, message = delete_crop(crop_id, farmer_id)

    return jsonify({
        "success": success,
        "message": message
    }), (200 if success else 400)