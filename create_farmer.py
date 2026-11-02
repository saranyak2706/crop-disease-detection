from getpass import getpass
from main import app
from models import db, Farmer
from werkzeug.security import generate_password_hash

with app.app_context():

    name = input("Enter farmer name: ")
    email = input("Enter farmer email: ")
    password = getpass("Enter farmer password: ")

    existing_farmer = Farmer.query.filter_by(
        email=email
    ).first()

    if existing_farmer:
        print("Farmer email already exists!")

    else:
        hashed_password = generate_password_hash(password)

        farmer = Farmer(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(farmer)
        db.session.commit()

        print("Farmer account created successfully!")