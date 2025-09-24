import os
import psycopg2
from flask import Flask, request, render_template
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

# ------------------- FLASK CONFIG -------------------
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------- SURYA OCR INIT -------------------
foundation_predictor = FoundationPredictor()
recognition_predictor = RecognitionPredictor(foundation_predictor)
detection_predictor = DetectionPredictor()

# ------------------- POSTGRES CONNECTION -------------------
# ⚠️ Update these values with your PostgreSQL credentials
conn = psycopg2.connect(
    host="localhost",
    database="certdb",
    user="postgres",
    password="sai3606"
)
cursor = conn.cursor()


# ------------------- OCR FUNCTION -------------------
def extract_fields(image_path):
    img = Image.open(image_path)
    predictions = recognition_predictor(
        [img], det_predictor=detection_predictor)

    fields = {}
    for page in predictions:
        for line in page.text_lines:
            text = line.text
            if "Name" in text:
                fields["Name"] = text.split(":")[-1].strip()
            if "Enrollment" in text:
                fields["Enrollment No"] = "".join(
                    [c for c in text if c.isdigit()])
            if "Credits" in text:
                fields["Credits"] = "".join([c for c in text if c.isdigit()])
            if "Percentage" in text:
                fields["Percentage"] = text.split()[-1].replace("%", "")

    return fields


# ------------------- DB CHECK -------------------
def check_with_db(fields):
    if "Enrollment No" not in fields:
        return "Enrollment number missing in OCR", False

    enrollment = fields["Enrollment No"]
    cursor.execute(
        "SELECT name, credits, percentage FROM students WHERE enrollment_no = %s", (enrollment,))
    record = cursor.fetchone()

    if not record:
        return f"No record found for enrollment {enrollment}", False

    db_name, db_credits, db_percentage = record
    mismatches = []

    if fields.get("Name") and fields["Name"].lower() != db_name.lower():
        mismatches.append("Name mismatch")
    if fields.get("Credits") and str(fields["Credits"]) != str(db_credits):
        mismatches.append("Credits mismatch")
    if fields.get("Percentage") and str(fields["Percentage"]) != str(db_percentage):
        mismatches.append("Percentage mismatch")

    if mismatches:
        return f"Suspicious ⚠️ → {', '.join(mismatches)}", False
    return "Authentic ✅", True


# ------------------- ROUTES -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # OCR
        fields = extract_fields(filepath)

        # DB check
        status, matched = check_with_db(fields)

        return render_template("result.html", fields=fields, status=status)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
