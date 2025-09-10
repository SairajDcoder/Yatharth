import random
import smtplib
import ssl
from flask_restx import Resource, Namespace
from flask import request, render_template, make_response, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import TelField, StringField, PasswordField, SubmitField, EmailField, BooleanField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, DataRequired, Optional


LOGIN_API = Namespace('account', description='login related operations')

smtp_port = 587
smtp_server = "smtp.gmail.com"
email_from = "transrectsalesandservices@gmail.com"
pswd = "fdzt ykhf ysfc xavb"


class MyForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=5, max=20, message="Username must be between 5 and 20 characters")
    ])

    email = EmailField('Email address', validators=[
        DataRequired(message="Email is required"),
        Email(message="Enter a valid email address")
    ])

    phone_number = TelField('Phone Number', validators=[
        DataRequired(message="Phone Number is required"),
        Length(min=10, max=10, message="Phone Number must be 10 digits")
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, max=8, message="Password must be 8 characters")
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Confirm Password is required"),
        EqualTo('password', message="Passwords must match"),
        Length(min=8, max=8, message="Confirm Password must be 8 characters")
    ])

    remember_me = BooleanField('Keep me Signed In')

    submit = SubmitField('Submit', render_kw={'class': 'submit-button'})

    def adjust_for_login(self):
        self.username.validators[:] = [Optional()]
        self.phone_number.validators[:] = [Optional()]
        self.confirm_password.validators[:] = [Optional()]

    def make_required(self):
        self.username.validators[:] = [
            DataRequired(message="Username is required"),
            Length(min=5, max=20,
                   message="Username must be between 5 and 20 characters")
        ]
        self.phone_number.validators[:] = [
            DataRequired(message="Phone Number is required"),
            Length(min=10, max=10, message="Phone Number must be 10 digits")
        ]
        self.confirm_password.validators[:] = [
            DataRequired(message="Confirm Password is required"),
            EqualTo('password', message="Passwords must match"),
            Length(min=8, max=8, message="Confirm Password must be 8 characters")
        ]


class VerificationForm(FlaskForm):
    email = EmailField('Email address', validators=[
        DataRequired(message="Email is required"),
        Email(message="Enter a valid email address")
    ])
    verification_code_0 = StringField('Code', [Optional(), Length(max=1)])
    verification_code_1 = StringField('Code', [Optional(), Length(max=1)])
    verification_code_2 = StringField('Code', [Optional(), Length(max=1)])
    verification_code_3 = StringField('Code', [Optional(), Length(max=1)])
    verification_code_4 = StringField('Code', [Optional(), Length(max=1)])
    verification_code_5 = StringField('Code', [Optional(), Length(max=1)])


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        'New Password', [DataRequired(), Length(min=8, max=8, message="Password must be 8 characters")])
    confirm_password = PasswordField(
        'Confirm Password', [EqualTo('new_password', message='Passwords must match'), Length(min=8, max=8, message="Password must be 8 characters")])


def send_email(recipient_email, subject, message):
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_from, pswd)
            email_message = f"Subject: {subject}\n\n{message}"
            server.sendmail(email_from, recipient_email, email_message)
            print(f"Email successfully sent to - {recipient_email}")
    except Exception as e:
        print(f"Error: {e}")


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))


@LOGIN_API.route('/login', methods=['GET', 'POST'])
class Login(Resource):
    def get(self):
        form = MyForm()
        form.adjust_for_login()
        if session.get('keep_signed_in') and session.get('email') == session.get('last_email'):
            if (session.get('last_email') == "transrectsalesandservices@gmail.com"):
                print(session.get('last_email'))
                return make_response(render_template('./admin/admin.html', form=form, admin=True))
            print(session.get('last_email'))
            return redirect(url_for('log.account_home'))
        return make_response(render_template('./loginhtml.html', form=form))

    def post(self):
        form = MyForm()
        form.adjust_for_login()
        if form.validate_on_submit():
            from src.yatharth.database.login_model import Login
            # from src.yatharth.database.admin_model import Admin
            flag = False
            log = Login.query.all()
            email = form.email.data
            password = form.password.data
            session['last_email'] = email
            if form.remember_me.data:
                session['keep_signed_in'] = True
            else:
                session['keep_signed_in'] = False
            session['email'] = email

            # admin = Admin.query.filter_by(
            #     email=email, password=password).first()
            # if admin:
            #     session['username'] = admin.name
            #     return make_response(render_template('./admin/admin.html', form=form, admin=True))

            u_email = None
            for data in log:
                if data.email == email and data.password == password:
                    flag = True
                    u_email = data.email
                    break
            if flag:
                flash('Successfully Logged In', 'success')
                myuser = Login.query.filter_by(email=email).first()
                if myuser:
                    session['username'] = myuser.username
                return redirect(url_for('log.communication_main'))
            else:
                flash('Incorrect email or password. Please try again.', 'error')
                print("Flash message triggered for incorrect credentials")
                return make_response(render_template('./loginhtml.html', form=form))

        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", "error")
        return make_response(render_template('./loginhtml.html', form=form))


@LOGIN_API.route('/logout')
class Logout(Resource):
    def get(self):
        session.pop('email', None)
        session.pop('keep_signed_in', None)
        session.pop('last_email', None)
        session.pop('username', None)
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('log.account_login'))


@LOGIN_API.route('/home')
class Home(Resource):
    def get(self):
        return redirect(url_for('log.communication_main'))


@LOGIN_API.route('/signup', methods=['GET', 'POST'])
class SignUp(Resource):
    def get(self):
        form = MyForm()
        form.make_required()
        return make_response(render_template('./signup.html', form=form))

    def post(self):
        from src.yatharth.database import db
        from src.yatharth.database.login_model import Login
        # from src.yatharth.database.user_model import User
        form = MyForm()
        form.make_required()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            phone_no = int(form.phone_number.data)
            password = form.password.data

            login = Login(username=username, email=email,
                          phone_no=phone_no, password=password)

            # user = User(username=username, email=email,
            #             phone_no=phone_no, password=password)

            db.session.add(login)
            # db.session.add(user)
            db.session.commit()
            flash('Account created successfully. Please login.', 'success')
            return make_response(render_template('./loginhtml.html', form=form))

        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", "error")
        return make_response(render_template('./signup.html', form=form))


@LOGIN_API.route('/forgot_password', methods=['GET', 'POST'])
class ForgotPassword(Resource):
    def get(self):
        form = VerificationForm()
        return make_response(render_template('forgot_password.html', form=form))

    def post(self):
        form = VerificationForm()
        action = request.form.get('action')
        email = form.email.data

        if action == 'send_email':
            if form.validate_on_submit():
                verification_code = generate_verification_code()
                session['verification_code'] = verification_code
                session['email'] = email
                subject = "Your Verification Code"
                message = f"Your verification code is: {verification_code}"
                send_email(email, subject, message)
                flash('Verification code sent to your email.', 'success')
                return make_response(render_template('forgot_password.html', form=form))
        elif action == 'verify_code':
            verification_code = ''.join([
                form.verification_code_0.data, form.verification_code_1.data,
                form.verification_code_2.data, form.verification_code_3.data,
                form.verification_code_4.data, form.verification_code_5.data
            ])
            if verification_code == session.get('verification_code'):
                return redirect(url_for('log.account_reset_password'))
            else:
                flash('Invalid verification code. Please try again.', 'error')

        return make_response(render_template('forgot_password.html', form=form))


@LOGIN_API.route('/verify_code', methods=['POST'])
class VerifyCode(Resource):
    def post(self):
        verification_code = ''.join([
            request.form.get('verification_code_0'), request.form.get(
                'verification_code_1'),
            request.form.get('verification_code_2'), request.form.get(
                'verification_code_3'),
            request.form.get('verification_code_4'), request.form.get(
                'verification_code_5')
        ])
        if verification_code == session.get('verification_code'):
            return redirect(url_for('log.account_reset_password'))
        else:
            flash('Invalid verification code. Please try again.', 'error')
            return redirect(url_for('log.account_forgot_password'))


@LOGIN_API.route('/resend_email')
class ResendEmail(Resource):
    def get(self):
        email = session.get('email')
        if email:
            verification_code = generate_verification_code()
            session['verification_code'] = verification_code
            subject = "Your New Verification Code"
            message = f"Your new verification code is: {verification_code}"
            send_email(email, subject, message)
            flash('New verification code sent to your email.', 'success')
        return redirect(url_for('log.account_forgot_password'))


@LOGIN_API.route('/reset_password', methods=['GET', 'POST'])
class ResetPassword(Resource):
    def get(self):
        form = ResetPasswordForm()
        return make_response(render_template('reset_password.html', form=form))

    def post(self):
        form = ResetPasswordForm()
        if form.validate_on_submit():
            email = session.get('email')
            new_password = form.new_password.data
            if (email != "transrectsalesandservices@gmail.com"):
                from src.yatharth.database import db
                from src.yatharth.database.login_model import Login
                user = Login.query.filter_by(email=email).first()
                if user:
                    user.password = new_password
                    db.session.commit()
                    flash(
                        'Password reset successfully. Please login with your new password.', 'success')
                else:
                    flash('User not found. Please try again.', 'error')
                return redirect(url_for('log.account_login'))
            else:
                # from src.yatharth.database import db
                # from src.yatharth.database.admin_model import Admin
                # admin = Admin.query.filter_by(email=email).first()
                # if admin:
                #     admin.password = new_password
                #     db.session.commit()
                #     flash(
                #         'Password reset successfully. Please login with your new password.', 'success')
                # else:
                flash('User not found. Please try again.', 'error')
                return redirect(url_for('log.account_login'))
        return make_response(render_template('reset_password.html', form=form))
