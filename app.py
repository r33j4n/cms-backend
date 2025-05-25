from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from rag_engine import get_solution_from_complaint, classify_complaint_domain
from dotenv import load_dotenv
from auth import auth_bp
from admin_routes import admin_bp
from database import init_db, db
from models import FlatOwner, Complaint, create_default_admin
from schemas import ComplaintCreate, FlatOwnerCreate
from cloud_storage import upload_image_to_cloudinary

load_dotenv()
app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True, allow_headers="*", methods=["GET", "POST", "PUT","PATCH", "DELETE", "OPTIONS"])
# Initialize database
init_db(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create default admin user
create_default_admin(app)

# Allowed file extensions for proof images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/complaint", methods=["POST"])
def handle_complaint():
    try:
        # Check if the request is multipart/form-data or application/json
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Get form data and validate using Pydantic model
            form_data = {
                "pin_no": request.form.get("pin_no", ""),
                "flat_no": request.form.get("flat_no", ""),
                "complaint": request.form.get("complaint", "")
            }
            complaint_data = ComplaintCreate(**form_data)

            # Verify flat owner credentials
            flat_owner = FlatOwner.query.filter_by(flat_no=complaint_data.flat_no).first()
            if not flat_owner:
                return jsonify({"error": "Flat not found. Please check your flat number."}), 404

            if flat_owner.pin_no != complaint_data.pin_no:
                return jsonify({"error": "Invalid PIN number. Please check your credentials."}), 401

            # Handle proof image upload
            proof_image_path = None
            if 'proof_image' in request.files:
                file = request.files['proof_image']
                if file and file.filename and allowed_file(file.filename):
                    # Upload image to Cloudinary
                    upload_result = upload_image_to_cloudinary(file)
                    if upload_result['success']:
                        proof_image_path = upload_result['url']
                    else:
                        # If Cloudinary upload fails, fall back to local storage
                        filename = secure_filename(file.filename)
                        # Add timestamp to filename to avoid duplicates
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        filename = f"{timestamp}_{filename}"
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        proof_image_path = f"/static/uploads/{filename}"

            complaint_text = complaint_data.complaint
        else:
            # Handle JSON request and validate using Pydantic model
            data = request.get_json()
            complaint_data = ComplaintCreate(**data)

            # Verify flat owner credentials
            flat_owner = FlatOwner.query.filter_by(flat_no=complaint_data.flat_no).first()
            if not flat_owner:
                return jsonify({"error": "Flat not found. Please check your flat number."}), 404

            if flat_owner.pin_no != complaint_data.pin_no:
                return jsonify({"error": "Invalid PIN number. Please check your credentials."}), 401

            proof_image_path = None
            complaint_text = complaint_data.complaint

        # Generate solution using RAG
        solution = get_solution_from_complaint(complaint_text)

        # Classify complaint domain
        domain = classify_complaint_domain(complaint_text)

        # Create and save complaint
        complaint = Complaint(
            description=complaint_text,
            owner_id=flat_owner.id,
            proof_image=proof_image_path
        )
        complaint.solution = solution
        complaint.domain = domain

        db.session.add(complaint)
        db.session.commit()

        return jsonify({
            "success": True,
            "complaint_id": complaint.id,
            "flat_no": complaint_data.flat_no,
            "complaint": complaint_text,
            "domain": domain,
            "solution": solution,
            "proof_image": proof_image_path
        })
    except ValueError as e:
        # Handle validation errors
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@app.route("/api/flat-owner", methods=["POST"])
def register_flat_owner():
    try:
        # Validate request data using Pydantic model
        data = request.get_json()
        flat_owner_data = FlatOwnerCreate(**data)

        # Check if flat number already exists
        existing_flat = FlatOwner.query.filter_by(flat_no=flat_owner_data.flat_no).first()
        if existing_flat:
            return jsonify({"error": "Flat number already registered"}), 409

        # Create and save flat owner
        flat_owner = FlatOwner(
            pin_no=flat_owner_data.pin_no,
            flat_no=flat_owner_data.flat_no,
            contact_no=flat_owner_data.contact_no
        )

        db.session.add(flat_owner)
        db.session.commit()

        return jsonify({
            "success": True,
            "flat_owner_id": flat_owner.id,
            "flat_no": flat_owner_data.flat_no,
            "message": "Flat owner registered successfully"
        })
    except ValueError as e:
        # Handle validation errors
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/complaints", methods=["GET"])
def get_public_complaints():
    """
    Get all complaints for public dashboard (without sensitive information)
    """
    try:
        complaints = Complaint.query.all()
        result = []

        for complaint in complaints:
            result.append({
                'id': complaint.id,
                'description': complaint.description,
                'domain': complaint.domain,
                'solution': complaint.solution,
                'is_checked': complaint.is_checked,
                'created_at': complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'proof_image': complaint.proof_image
            })

        return jsonify({'complaints': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/")
def index():
    return "Welcome to the Apartment Complaint Assistant API! Use /api/complaint to submit a complaint."

if __name__ == "__main__":
    app.run(debug=True)
