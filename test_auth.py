import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_system():
    # Test data
    test_user = {
        "email": "test2@example.com",
        "password": "secure_password123"
    }
    
    print("\n=== Testing Authentication System ===\n")
    
    # 1. Test Registration
    print("1. Testing Registration...")
    try:
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user
        )
        register_response.raise_for_status()
        print("✅ Registration successful!")
        print("Response:", json.dumps(register_response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("❌ Registration failed:", str(e))
        return
    
    # 2. Test Successful Login
    print("\n2. Testing Successful Login...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=test_user
        )
        login_response.raise_for_status()
        print("✅ Login successful!")
        print("Response:", json.dumps(login_response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("❌ Login failed:", str(e))
        return
    
    # 3. Test Failed Login - Wrong Password
    print("\n3. Testing Failed Login (Wrong Password)...")
    try:
        wrong_password = test_user.copy()
        wrong_password["password"] = "wrong_password"
        failed_login = requests.post(
            f"{BASE_URL}/auth/login",
            json=wrong_password
        )
        print(f"✅ Failed login handled correctly! Status code: {failed_login.status_code}")
        print("Response:", json.dumps(failed_login.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("❌ Failed login test error:", str(e))
    
    # 4. Test Failed Login - Wrong Email
    print("\n4. Testing Failed Login (Wrong Email)...")
    try:
        wrong_email = test_user.copy()
        wrong_email["email"] = "nonexistent@example.com"
        failed_login = requests.post(
            f"{BASE_URL}/auth/login",
            json=wrong_email
        )
        print(f"✅ Failed login handled correctly! Status code: {failed_login.status_code}")
        print("Response:", json.dumps(failed_login.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("❌ Failed login test error:", str(e))

if __name__ == "__main__":
    test_auth_system() 