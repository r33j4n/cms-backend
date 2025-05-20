from flask import Flask, request, jsonify
from flask_cors import CORS

from rag_engine import get_solution_from_complaint  # <- import only 1 function
from dotenv import load_dotenv
from auth import auth_bp
import os

load_dotenv()
app = Flask(__name__)
app.register_blueprint(auth_bp)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all for now, or specify your React domain


@app.route("/api/complaint", methods=["POST"])
def handle_complaint():
    data = request.get_json()
    nic = data.get("nic")
    apartment_no = data.get("apartment_no")
    complaint_text = data.get("complaint")
    if not nic or not apartment_no or not complaint_text:
        return jsonify({"error": "All fields are required"}), 400
    try:
        solution = get_solution_from_complaint(complaint_text)
        return jsonify({
            "nic": nic,
            "apartment_no": apartment_no,
            "complaint": complaint_text,
            "solution": solution
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/")
def index():
    return "Welcome to the Apartment Complaint Assistant API! Use /api/complaint to submit a complaint."

if __name__ == "__main__":
    app.run(debug=True)