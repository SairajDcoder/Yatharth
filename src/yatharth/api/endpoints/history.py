from flask import request, jsonify, session
from flask_restx import Resource, Namespace
from src.yatharth.database import db
from src.yatharth.database.verifyHistory_model import VerificationHistory

# Using a new name as requested to avoid conflicts
HISTORY_API = Namespace(
    'history', description='Verification history operations')


@HISTORY_API.route('/save')
class SaveHistory(Resource):
    def post(self):
        if 'email' not in session:
            return jsonify({"success": False, "message": "User not authenticated."}), 401

        data = request.get_json()
        user_email = session['email']

        # MODIFICATION: Added the missing fields to the required list
        required_fields = ['student_name', 'institution',
                           'degree', 'status', 'certificate_id', 'issue_date']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": "Missing required data to save history."}), 400

        try:
            new_entry = VerificationHistory(
                user_email=user_email,
                student_name=data['student_name'],
                institution=data['institution'],
                degree=data['degree'],
                verification_status=data['status'],
                # MODIFICATION: Added the missing attributes
                certificate_id=data['certificate_id'],
                issue_date=data['issue_date']
            )
            db.session.add(new_entry)
            db.session.commit()
            return jsonify({"success": True, "message": "Verification history saved."})
        except Exception as e:
            db.session.rollback()
            print(f"DATABASE ERROR on history save: {e}")
            return jsonify({"success": False, "message": "Could not save history to database."}), 500


@HISTORY_API.route('/list')
class GetHistory(Resource):
    def get(self):
        # This endpoint fetches the 5 most recent verifications for the homepage
        try:
            recent_verifications = VerificationHistory.query.order_by(
                VerificationHistory.verified_at.desc()
            ).limit(5).all()

            # Use the to_dict() method to convert the database objects to a clean list
            history_list = [item.to_dict() for item in recent_verifications]

            return jsonify({"success": True, "history": history_list})
        except Exception as e:
            print(f"DATABASE ERROR on fetching history: {e}")
            return jsonify({"success": False, "message": "Could not fetch verification history."}), 500
