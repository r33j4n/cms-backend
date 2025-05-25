# CMS Backend - Simplified Authentication

This repository contains a Flask-based backend for a Complaint Management System (CMS) with simplified authentication.

## Changes Made

1. **Simplified Authentication**:
   - Removed session-based authentication
   - Removed cookie requirements
   - Implemented a simple login endpoint for flat owners
   - Disabled admin authentication checks (admin_required decorator is now a pass-through)

2. **Cloud Storage Integration**:
   - Added Cloudinary integration for storing proof images
   - Images are now uploaded to Cloudinary instead of being stored locally
   - Fallback to local storage if Cloudinary upload fails

3. **API Endpoints**:
   - `/api/login` - Flat owner login
   - `/api/flat-owner` - Register a new flat owner
   - `/api/complaint` - Submit a complaint
   - `/api/complaints` - Get all public complaints

## Setup and Testing

1. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **Set up Cloudinary**:
   - Sign up for a free Cloudinary account at https://cloudinary.com/
   - Get your Cloud Name, API Key, and API Secret from the Cloudinary dashboard
   - Update the `.env` file with your Cloudinary credentials:
     ```
     CLOUDINARY_CLOUD_NAME=your_cloud_name
     CLOUDINARY_API_KEY=your_api_key
     CLOUDINARY_API_SECRET=your_api_secret
     ```

3. **Run the application**:
   ```
   python app.py
   ```

4. **Test the login functionality**:
   ```
   python test_login.py
   ```
   Note: You may need to modify the test credentials in `test_login.py` to match an existing flat owner in your database.

5. **Test other APIs**:
   ```
   python test_apis.py
   ```
   This script will:
   - Register a new flat owner
   - Submit a complaint using the newly registered flat owner
   - Retrieve all public complaints

## Future Improvements

1. Implement proper authentication with tokens (JWT)
2. Add proper admin authentication when needed
3. Implement cookie-based authentication for web clients
4. Enhance cloud storage integration with additional features:
   - Image optimization and resizing
   - Support for video uploads
   - Implement a media management interface
