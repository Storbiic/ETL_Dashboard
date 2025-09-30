#!/usr/bin/env python3
"""
Test script to verify GCP Cloud Run port configuration
"""
import os
import sys
import subprocess
import time
import requests

def test_local_docker():
    """Test the Docker image locally with Cloud Run port configuration"""
    print("🧪 Testing Docker image locally with PORT=8080...")
    
    # Stop any existing container
    subprocess.run(["docker", "stop", "test-frontend"], capture_output=True)
    subprocess.run(["docker", "rm", "test-frontend"], capture_output=True)
    
    try:
        # Run container with Cloud Run configuration
        cmd = [
            "docker", "run", "-d",
            "--name", "test-frontend",
            "-p", "8080:8080",
            "-e", "PORT=8080",
            "-e", "FLASK_ENV=production",
            "-e", "PYTHONPATH=/app",
            "etl-frontend-gcp:test"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to start container: {result.stderr}")
            return False
        
        print("⏳ Waiting for container to start...")
        time.sleep(10)
        
        # Test the endpoint
        try:
            response = requests.get("http://localhost:8080/", timeout=10)
            if response.status_code == 200:
                print("✅ Container is responding on port 8080!")
                print(f"📊 Response length: {len(response.text)} chars")
                return True
            else:
                print(f"❌ Container responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to container: {e}")
            return False
        
    finally:
        # Cleanup
        subprocess.run(["docker", "stop", "test-frontend"], capture_output=True)
        subprocess.run(["docker", "rm", "test-frontend"], capture_output=True)

def check_dockerfile():
    """Check if Dockerfile has correct port configuration"""
    print("🔍 Checking Dockerfile configuration...")
    
    with open("Dockerfile.frontend", "r") as f:
        content = f.read()
    
    checks = {
        "PORT environment variable": "ENV PORT=8080" in content,
        "Dynamic port in CMD": "${PORT:-8080}" in content,
        "Expose port variable": "EXPOSE $PORT" in content
    }
    
    all_good = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            all_good = False
    
    return all_good

def main():
    print("🔧 GCP Cloud Run Port Configuration Test")
    print("=" * 50)
    
    # Check Dockerfile
    dockerfile_ok = check_dockerfile()
    
    if not dockerfile_ok:
        print("\n❌ Dockerfile configuration issues found!")
        return 1
    
    print("\n✅ Dockerfile configuration looks good!")
    print("\n💡 To test locally, run:")
    print("   docker build -f Dockerfile.frontend -t etl-frontend-gcp:test .")
    print("   python test_gcp_config.py")
    
    print("\n🚀 To deploy to GCP Cloud Run:")
    print("   PowerShell: .\\deploy-frontend-gcp.ps1")
    print("   Bash: ./deploy-frontend-gcp.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())