
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app
)
from werkzeug.security import generate_password_hash

from models import db, Farmer
from services.email_service import (
    generate_reset_token,
    verify_reset_token,
    send_reset_email
)

reset_bp = Blueprint(
    'password_reset',
    __name__,
    url_prefix='/auth'
)


# Forgot Password - Request reset email
@reset_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form.get('email', '').strip()

        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('forgot_password.html')

        farmer = Farmer.query.filter_by(email=email).first()

        # Use a generic response to avoid revealing whether an account exists
        if farmer:
            token = generate_reset_token(farmer.email)

            reset_url = url_for(
                'password_reset.reset_password',
                token=token,
                _external=True
            )

            send_reset_email(
                farmer.email,
                farmer.name or 'Farmer',
                reset_url
            )

        flash(
            'If an account exists for that email, a reset link will be sent.',
            'info'
        )
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


# Reset Password
@reset_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):

    email = verify_reset_token(token)

    if not email:
        flash('Password reset link is invalid or expired.', 'danger')
        return redirect(url_for('auth.login'))

    farmer = Farmer.query.filter_by(email=email).first()

    if not farmer:
        flash('Account not found.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':

        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('reset_password.html')

        if len(password) < 8:
            flash('Password must contain at least 8 characters.', 'danger')
            return render_template('reset_password.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html')

        farmer.password = generate_password_hash(password)
        db.session.commit()

        flash('Password reset successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
