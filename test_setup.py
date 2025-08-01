#!/usr/bin/env python3
"""
Test script to verify the Text Processing Tool setup (FastAPI version)
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('openai', 'OpenAI'),
        ('pydantic', 'Pydantic'),
        ('dotenv', 'python-dotenv')
    ]
    
    failed_imports = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed_imports.append(name)
    
    return len(failed_imports) == 0

def test_files():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'app.py',
        'index.html',
        'styles.css',
        'script.js',
        'requirements.txt',
        'start.py',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_app_startup():
    """Test if the FastAPI app can be imported and configured"""
    print("\n🚀 Testing FastAPI app configuration...")
    
    try:
        from app import app, text_processor
        print("  ✅ FastAPI app imported successfully")
        
        # Test app configuration
        if hasattr(app, 'title'):
            print(f"  ✅ FastAPI app configured: {app.title}")
        
        # Test text processor
        if hasattr(text_processor, 'split_text'):
            print("  ✅ TextProcessor class initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Text Processing Tool - Setup Verification (FastAPI)")
    print("=" * 55)
    
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Run tests
    imports_ok = test_imports()
    files_ok = test_files()
    app_ok = test_app_startup()
    
    print("\n" + "=" * 55)
    print("📊 Test Results:")
    print(f"  Package imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  File structure: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"  FastAPI app: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if imports_ok and files_ok and app_ok:
        print("\n🎉 All tests passed! The FastAPI application is ready to run.")
        print("\nTo start the application:")
        print("  python start.py")
        print("  # OR")
        print("  python app.py")
        print("  # OR")
        print("  uvicorn app:app --host 0.0.0.0 --port 8000")
        print("\nThen open: http://localhost:8000")
        print("API docs: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        if not imports_ok:
            print("  - Install missing packages: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit(main())