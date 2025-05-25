from flask import Blueprint, request, jsonify
from auth import admin_required
from models import Complaint, FlatOwner
from database import db
from schemas import ComplaintResponse, FlatOwnerResponse
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/api/admin/complaints', methods=['GET'])
@admin_required
def get_all_complaints():
    """
    Get all complaints for admin dashboard
    """
    try:
        complaints = Complaint.query.all()
        result = []

        for complaint in complaints:
            flat_owner = FlatOwner.query.get(complaint.owner_id)
            result.append({
                'id': complaint.id,
                'description': complaint.description,
                'domain': complaint.domain,
                'solution': complaint.solution,
                'is_checked': complaint.is_checked,
                'created_at': complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'proof_image': complaint.proof_image,
                'flat_no': flat_owner.flat_no,
                'contact_no': flat_owner.contact_no
            })

        return jsonify({'complaints': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/complaints/<int:complaint_id>/toggle-checked', methods=['PATCH'])
@admin_required
def toggle_complaint_check(complaint_id):
    """
    Toggle the is_checked status of a complaint
    """
    try:
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return jsonify({'error': 'Complaint not found'}), 404

        complaint.is_checked = not complaint.is_checked
        db.session.commit()

        return jsonify({
            'success': True,
            'complaint_id': complaint.id,
            'is_checked': complaint.is_checked
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/complaints/<int:complaint_id>', methods=['GET'])
@admin_required
def get_complaint_details(complaint_id):
    """
    Get detailed information about a specific complaint
    """
    try:
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return jsonify({'error': 'Complaint not found'}), 404

        flat_owner = FlatOwner.query.get(complaint.owner_id)

        result = {
            'id': complaint.id,
            'description': complaint.description,
            'domain': complaint.domain,
            'solution': complaint.solution,
            'is_checked': complaint.is_checked,
            'created_at': complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'proof_image': complaint.proof_image,
            'flat_owner': {
                'id': flat_owner.id,
                'flat_no': flat_owner.flat_no,
                'contact_no': flat_owner.contact_no
            }
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/flat-owners', methods=['GET'])
@admin_required
def get_all_flat_owners():
    """
    Get all flat owners for admin dashboard
    """
    try:
        flat_owners = FlatOwner.query.all()
        result = []

        for owner in flat_owners:
            result.append({
                'id': owner.id,
                'flat_no': owner.flat_no,
                'contact_no': owner.contact_no,
                'complaint_count': len(owner.complaints)
            })

        return jsonify({'flat_owners': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/dashboard-stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """
    Get statistics for admin dashboard
    Returns counts of complaints by domain and by flat number
    """
    try:
        # Get domain counts
        domain_counts_query = db.session.query(
            Complaint.domain,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.domain).order_by(func.count(Complaint.id).desc()).all()

        domain_counts = [
            {"domain": domain, "count": count} 
            for domain, count in domain_counts_query
            if domain is not None  # Filter out None domains
        ]

        # Get flat counts
        flat_counts_query = db.session.query(
            FlatOwner.flat_no,
            func.count(Complaint.id).label('count')
        ).join(
            Complaint, Complaint.owner_id == FlatOwner.id
        ).group_by(
            FlatOwner.flat_no
        ).order_by(
            func.count(Complaint.id).desc()
        ).all()

        flat_counts = [
            {"flat_no": flat_no, "count": count}
            for flat_no, count in flat_counts_query
        ]

        return jsonify({
            "domain_counts": domain_counts,
            "flat_counts": flat_counts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
