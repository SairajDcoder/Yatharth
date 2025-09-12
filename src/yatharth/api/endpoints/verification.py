import os
import psycopg2
from flask_restx import Resource, Namespace
from flask import request, jsonify, current_app
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

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
        database="certdb",
        user="postgres",
        password="sai3606"
    )
    return conn, conn.cursor()

# --- OCR FUNCTION ---


def extract_fields(image_path):
    img = Image.open(image_path)
    predictions = recognition_predictor(
        [img], det_predictor=detection_predictor)

    fields = {}
    for page in predictions:
        for line in page.text_lines:
            text = line.text
            if "Name" in text:
                fields["name"] = text.split(":")[-1].strip()
            if "Enrollment" in text:
                fields["enrollment_no"] = "".join(
                    [c for c in text if c.isdigit()])
            if "Credits" in text:
                fields["credits"] = "".join([c for c in text if c.isdigit()])
            if "Percentage" in text:
                fields["percentage"] = text.split()[-1].replace("%", "")

    return fields

# --- DB CHECK ---


def check_with_db(fields):
    conn, cursor = get_db_cursor()

    if "enrollment_no" not in fields:
        return {"status": "Error", "message": "Enrollment number missing in OCR"}

    enrollment = fields["enrollment_no"]
    cursor.execute(
        "SELECT name, credits, percentage FROM students WHERE enrollment_no = %s", (
            enrollment,)
    )
    record = cursor.fetchone()
    conn.close()

    if not record:
        return {"status": "Fraud Detected", "message": f"No record found for enrollment {enrollment}"}

    db_name, db_credits, db_percentage = record
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
        "message": "Authentic ✅",
        "name": db_name,
        "enrollment_no": enrollment,
        "credits": db_credits,
        "percentage": db_percentage
    }


@VERIFICATION_API.route('/', methods=['POST'])
class DocumentVerification(Resource):
    def post(self):
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filepath = os.path.join(
                current_app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Perform OCR and DB check
            extracted_fields = extract_fields(filepath)
            verification_result = check_with_db(extracted_fields)

            # Clean up the temporary file
            os.remove(filepath)

            return jsonify(verification_result)

        return jsonify({'error': 'File not processed'}), 500
