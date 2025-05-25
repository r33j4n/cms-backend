import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def upload_image_to_cloudinary(file, folder="complaint_proofs"):
    """
    Upload an image to Cloudinary
    
    Args:
        file: The file object to upload
        folder: The folder in Cloudinary to store the image (default: "complaint_proofs")
        
    Returns:
        dict: A dictionary containing the upload result, including the URL of the uploaded image
    """
    try:
        # Upload the image to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"
        )
        
        # Return the secure URL of the uploaded image
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }