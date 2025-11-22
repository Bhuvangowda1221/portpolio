#!/usr/bin/env python3
"""
Simple test script for the Flask portfolio app
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, Project

def simple_test():
    """Test basic app functionality"""
    print("Testing Flask Portfolio App...")
    
    with app.app_context():
        # Test database connection
        try:
            db.create_all()
            print("[OK] Database connection successful")
        except Exception as e:
            print(f"[ERROR] Database error: {e}")
            return False
        
        # Test project count
        try:
            count = Project.query.count()
            print(f"[OK] Found {count} projects in database")
            
            # Show project titles
            projects = Project.query.limit(3).all()
            for project in projects:
                print(f"  - {project.title}")
                
        except Exception as e:
            print(f"[ERROR] Project query error: {e}")
            return False
        
        # Test app configuration
        try:
            secret_key = app.config.get('SECRET_KEY')
            upload_folder = app.config.get('UPLOAD_FOLDER')
            admin_password = app.config.get('ADMIN_PASSWORD')
            print(f"[OK] App configured with secret key: {secret_key[:10]}...")
            print(f"[OK] Upload folder: {upload_folder}")
            print(f"[OK] Admin password configured: {admin_password}")
        except Exception as e:
            print(f"[ERROR] Configuration error: {e}")
            return False
    
    print("\n[SUCCESS] Basic tests passed! Your Flask portfolio app is configured correctly.")
    print("\nTo run the app:")
    print("1. cd c:\\Users\\Lenovo\\Coding\\portfolio_flask_app")
    print("2. python app.py")
    print("3. Open http://127.0.0.1:5000 in your browser")
    print(f"\nAdmin login password: {app.config.get('ADMIN_PASSWORD')}")
    return True

if __name__ == '__main__':
    simple_test()