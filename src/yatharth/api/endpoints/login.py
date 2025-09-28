import random
import smtplib
import ssl
from flask_restx import Resource, Namespace
from flask import request, render_template, make_response, flash, redirect, url_for, session, jsonify
from flask_wtf import FlaskForm
from wtforms import TelField, StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import Length, Email, EqualTo, DataRequired
from src.yatharth.database.login_model import Login as LoginModel
from src.yatharth.database.admin import AdminLogin
from src.yatharth.database import db
from werkzeug.security import generate_password_hash, check_password_hash

LOGIN_API = Namespace('account', description='login related operations')

smtp_port = 587
smtp_server = "smtp.gmail.com"
email_from = "transrectsalesandservices@gmail.com"
pswd = "fdzt ykhf ysfc xavb"

# --- Form Definitions ---


class LoginForm(FlaskForm):
    email = EmailField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me Signed In')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=4, max=25)])
    email = EmailField('Email address', validators=[DataRequired(), Email()])
    phone_number = TelField('Phone Number', validators=[
                            DataRequired(), Length(min=10, max=10)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])


class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email address', validators=[DataRequired(), Email()])

# MODIFIED: Added form for OTP verification


class VerifyCodeForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[
                                    DataRequired(), Length(min=6, max=6)])

# MODIFIED: Added form for the final password reset


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
                                 DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('new_password')])


def send_email(recipient_email, subject, message):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_from, pswd)
            email_message = f"Subject: {subject}\n\n{message}"
            server.sendmail(email_from, recipient_email, email_message)
    except Exception as e:
        print(f"Error sending email: {e}")


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))

# --- API Endpoints ---


@LOGIN_API.route('/login', methods=['POST'])
class Login(Resource):
    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            admin_user = AdminLogin.query.filter_by(email=email).first()

            if admin_user and check_password_hash(admin_user.password, password):
                session['email'] = admin_user.email
                session['is_admin'] = True
                session.permanent = form.remember_me.data

                return jsonify({
                    "success": True,
                    "message": "Admin login successful!",
                    "redirect_url": url_for('admin')
                })

            regular_user = LoginModel.query.filter_by(email=email).first()

            if regular_user and check_password_hash(regular_user.password, password):
                session['email'] = regular_user.email
                session['username'] = regular_user.username
                session['is_admin'] = False
                session.permanent = form.remember_me.data

                return jsonify({
                    "success": True,
                    "message": "Login successful!",
                    "redirect_url": url_for('index'),
                    "username": regular_user.username
                })

            return jsonify({"success": False, "message": "Incorrect email or password."})

        return jsonify({"success": False, "message": "Invalid form submission.", "errors": form.errors})


@LOGIN_API.route('/signup', methods=['POST'])
class SignUp(Resource):
    def post(self):
        form = SignUpForm()
        if form.validate_on_submit():
            if LoginModel.query.filter_by(email=form.email.data).first():
                return jsonify({"success": False, "message": "An account with this email already exists."})
            if LoginModel.query.filter_by(username=form.username.data).first():
                return jsonify({"success": False, "message": "This username is already taken."})
            if LoginModel.query.filter_by(phone_no=form.phone_number.data).first():
                return jsonify({"success": False, "message": "This phone number is already registered."})

            try:
                hashed_password = generate_password_hash(
                    form.password.data, method='pbkdf2:sha256')
                print(form.username.data + form.email.data +
                      form.phone_number.data + hashed_password)
                new_user = LoginModel(username=form.username.data, email=form.email.data,
                                      phone_no=form.phone_number.data, password=hashed_password)
                print("hello")

                db.session.add(new_user)
                db.session.commit()

                session['email'] = new_user.email
                session['username'] = new_user.username
                return jsonify({"success": True, "message": "Account created successfully!", "redirect_url": url_for('index')})
            except Exception as e:
                db.session.rollback()
                print(f"DATABASE SIGNUP ERROR: {e}")
                return jsonify({"success": False, "message": "A database error occurred. Please try again later."})

        return jsonify({"success": False, "message": "Please correct the form errors.", "errors": form.errors})


@LOGIN_API.route('/logout')
class Logout(Resource):
    def get(self):
        session.clear()
        return redirect(url_for('index'))


@LOGIN_API.route('/forgot_password', methods=['POST'])
class ForgotPassword(Resource):
    def post(self):
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            email = form.email.data
            user = LoginModel.query.filter_by(email=email).first()
            if not user:
                return jsonify({"success": False, "message": "No account found with that email address."})

            verification_code = generate_verification_code()
            session['verification_code'] = verification_code
            session['reset_email'] = email

            subject = "Your Password Reset Code"
            message = f"Your verification code is: {verification_code}"
            send_email(email, subject, message)

            return jsonify({"success": True, "message": "A verification code has been sent to your email."})
        return jsonify({"success": False, "message": "Please enter a valid email.", "errors": form.errors})

# MODIFIED: New endpoint to verify the OTP code


@LOGIN_API.route('/verify_code', methods=['POST'])
class VerifyCode(Resource):
    def post(self):
        form = VerifyCodeForm()
        if form.validate_on_submit():
            user_code = form.verification_code.data
            server_code = session.get('verification_code')

            if user_code == server_code:
                # Set a flag to allow password reset
                session['code_verified'] = True
                return jsonify({"success": True, "message": "Code verified successfully."})
            else:
                return jsonify({"success": False, "message": "Invalid verification code."})
        return jsonify({"success": False, "message": "Invalid submission.", "errors": form.errors})


# MODIFIED: New endpoint to handle the final password reset
@LOGIN_API.route('/reset_password', methods=['POST'])
class ResetPassword(Resource):
    def post(self):
        if not session.get('code_verified'):
            return jsonify({"success": False, "message": "Please verify your code first."})

        form = ResetPasswordForm()
        if form.validate_on_submit():
            email = session.get('reset_email')
            user = LoginModel.query.filter_by(email=email).first()
            if user:
                hashed_password = generate_password_hash(
                    form.new_password.data, method='pbkdf2:sha256')
                user.password = hashed_password
                db.session.commit()

                # Clear session variables related to reset
                session.pop('reset_email', None)
                session.pop('verification_code', None)
                session.pop('code_verified', None)

                return jsonify({"success": True, "message": "Password has been reset successfully. Please log in."})
            else:
                return jsonify({"success": False, "message": "User not found."})
        return jsonify({"success": False, "message": "Invalid submission.", "errors": form.errors})
