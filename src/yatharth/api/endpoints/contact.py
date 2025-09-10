from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

import smtplib
import ssl
from flask_restx import Resource, Namespace
from flask import request, render_template, make_response, flash, redirect, url_for, session


CONTACT_API = Namespace(
    'communication', description='for communication purpose')

smtp_port = 587
smtp_server = "smtp.gmail.com"
email_from = "transrectsalesandservices@gmail.com"
pswd = "fdzt ykhf ysfc xavb"


class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()], render_kw={
                       "placeholder": "Your Name", "class": "form-control"})
    email = StringField('Your Email', validators=[DataRequired(), Email()], render_kw={
                        "placeholder": "Your Email", "class": "form-control"})
    subject = StringField('Subject', validators=[DataRequired()], render_kw={
                          "placeholder": "Subject", "class": "form-control"})
    message = TextAreaField('Message', validators=[DataRequired()], render_kw={
                            "placeholder": "Message", "class": "form-control", "rows": "6"})
    submit = SubmitField('Send Message', render_kw={
                         "class": "btn btn-success"})


@CONTACT_API.route('/main', methods=['GET', 'POST'])
class Main(Resource):
    def get(self):
        contact_form = ContactForm()
        return make_response(render_template('index.html', contact_form=contact_form))

    def post(self):
        contact_form = ContactForm()
        if contact_form.validate_on_submit():
            recipient_email = "transrectsalesandservices@gmail.com"
            subject = contact_form.subject.data
            message = f"Name: {contact_form.name.data}\nEmail: {contact_form.email.data}\n\n{contact_form.message.data}"

            send_email(recipient_email, subject, message)
            flash("Your message has been sent successfully!", "success")
            # Redirect to the contact page
            return make_response(render_template('index.html', contact_form=contact_form))

        flash("Your message could not be sent. Please try again.", "error")
        return make_response(render_template('index.html', contact_form=contact_form))


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
