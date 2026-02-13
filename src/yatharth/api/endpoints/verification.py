import os
import psycopg2
from flask_restx import Resource, Namespace
from flask import request, jsonify, current_app
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from flask import session  # To check if a user is logged in
from src.yatharth.database import db  # Your main SQLAlchemy database instance
# The history table model
from src.yatharth.database.verifyHistory_model import VerificationHistory

VERIFICATION_API = Namespace(
    'verify', description='Credential verification operations')

# Initialize OCR predictors once
foundation_predictor = FoundationPredictor()
recognition_predictor = RecognitionPredictor(foundation_predictor)
detection_predictor = DetectionPredictor()

# --- POSTGRES CONNECTION ---
# Using the app context to manage the connection


def get_db_cursor():
    conn = psycopg2.connect(
        host="localhost",
        database="YatharthDB",
        user="postgres",
        password="sai3606"
    )
    return conn, conn.cursor()


# --- OCR FUNCTION ---


import io

def extract_fields(img):
    # img is now a PIL Image object
    predictions = recognition_predictor(
        [img], det_predictor=detection_predictor)

    fields = {}
    for page in predictions:
        for line in page.text_lines:
            text_content = line.text
            # Convert to lowercase for case-insensitive matching
            text_lower = text_content.lower()

            # Use .split(':', 1) to only split on the first colon, in case the value has a colon
            if "name" in text_lower:
                fields["student_name"] = text_content.split(':', 1)[-1].strip()
            if "enrollment" in text_lower:
                fields["enrollment_no"] = "".join(
                    [c for c in text_content if c.isdigit()])
            # Add keys for the history table
            if "degree" in text_lower or "bachelor" in text_lower or "master" in text_lower:
                fields["degree"] = text_content.split(':', 1)[-1].strip()
            if "university" in text_lower or "institute" in text_lower:
                fields["institution"] = text_content.split(':', 1)[-1].strip()

    return fields

# --- DB CHECK ---


def check_with_db(fields):
    conn, cursor = get_db_cursor()

    if "enrollment_no" not in fields:
        return {"status": "Error", "message": "Enrollment number missing in OCR"}

    enrollment = fields["enrollment_no"]
    cursor.execute(
        "SELECT student_name, credits, percentage, degree FROM students WHERE enrollment_no = %s", (
            enrollment,)
    )
    record = cursor.fetchone()
    conn.close()

    if not record:
        return {"status": "Fraud Detected", "message": f"No record found for enrollment {enrollment}"}

    db_name, db_credits, db_percentage, db_degree = record
    mismatches = []

    # Compare OCR fields with database records
    if fields.get("name") and fields["name"].lower() != db_name.lower():
        mismatches.append("Name mismatch")
    if fields.get("credits") and str(fields["credits"]) != str(db_credits):
        mismatches.append("Credits mismatch")
    if fields.get("percentage") and str(fields["percentage"]) != str(db_percentage):
        mismatches.append("Percentage mismatch")

    if mismatches:
        return {"status": "Suspicious", "message": f"Suspicious ⚠️ → {', '.join(mismatches)}"}

    return {
        "status": "Verified",
        "message": "Document appears to be authentic.",
        "student_name": db_name,
        "degree": db_degree,
        "enrollment_no": enrollment,
        # Pass through the institution name extracted by the OCR
        "institution": fields.get("institution", "Not Found")
    }


# Changed route for clarity
@VERIFICATION_API.route('/process', methods=['POST'])
class DocumentVerification(Resource):
    def post(self):
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400

        if file:
            try:
                # Read the file directly into memory as bytes
                file_bytes = file.read()
                # Create a PIL Image from the bytes
                img = Image.open(io.BytesIO(file_bytes))

                # Pass the PIL Image directly to the extractor
                extracted_fields = extract_fields(img)
                verification_result = check_with_db(extracted_fields)

                # MODIFICATION: We are REMOVING the history saving logic from this file.
                # The frontend will now be responsible for calling the /history/save endpoint.

            except Exception as e:
                print(f"VERIFICATION PROCESSING ERROR: {e}")
                verification_result = {"success": False, "status": "Error",
                                       "message": "A server error occurred during processing."}
            
            # No need for finally block or file cleanup since we didn't save to disk

            return jsonify(verification_result)

        return jsonify({'success': False, 'message': 'File could not be processed'}), 500
