import requests
import sys
import json
from datetime import datetime

class MonthlyReportsHubAPITester:
    def __init__(self, base_url="https://reports-auth-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.test_user_id = None
        self.location_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, expect_json=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if expect_json:
                    try:
                        response_data = response.json()
                        print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                        return True, response_data
                    except:
                        return True, {}
                else:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"username": "admin", "password": "admin123"}
        )
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin token obtained: {self.admin_token[:20]}...")
            return True
        return False

    def test_get_locations(self):
        """Test getting locations (public endpoint)"""
        success, response = self.run_test(
            "Get Locations",
            "GET",
            "locations",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            self.location_id = response[0]['id']
            print(f"   Found location: {response[0]['name']} (ID: {self.location_id})")
            return True
        return success

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "TestPass123!",
            "location_id": self.location_id
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        if success and 'id' in response:
            self.test_user_id = response['id']
            self.test_username = test_user_data['username']
            self.test_password = test_user_data['password']
            print(f"   User registered: {self.test_username} (ID: {self.test_user_id})")
            return True
        return False

    def test_user_login_before_approval(self):
        """Test user login before approval (should fail)"""
        success, response = self.run_test(
            "User Login Before Approval",
            "POST",
            "auth/login",
            403,  # Should be forbidden
            data={"username": self.test_username, "password": self.test_password}
        )
        return success  # Success means we got the expected 403 status

    def test_get_current_user_admin(self):
        """Test getting current user info for admin"""
        return self.run_test(
            "Get Current User (Admin)",
            "GET",
            "auth/me",
            200,
            token=self.admin_token
        )

    def test_get_all_users_admin(self):
        """Test getting all users (admin only)"""
        return self.run_test(
            "Get All Users (Admin)",
            "GET",
            "admin/users",
            200,
            token=self.admin_token
        )

    def test_approve_user(self):
        """Test approving a user (admin only)"""
        if not self.test_user_id:
            print("❌ No test user ID available for approval")
            return False
            
        success, response = self.run_test(
            "Approve User",
            "PUT",
            f"admin/users/{self.test_user_id}/approve",
            200,
            token=self.admin_token
        )
        return success

    def test_user_login_after_approval(self):
        """Test user login after approval (should succeed)"""
        success, response = self.run_test(
            "User Login After Approval",
            "POST",
            "auth/login",
            200,
            data={"username": self.test_username, "password": self.test_password}
        )
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            print(f"   User token obtained: {self.user_token[:20]}...")
            return True
        return False

    def test_get_current_user_regular(self):
        """Test getting current user info for regular user"""
        return self.run_test(
            "Get Current User (Regular)",
            "GET",
            "auth/me",
            200,
            token=self.user_token
        )

    def test_protected_route(self):
        """Test protected route with user token"""
        return self.run_test(
            "Protected Route",
            "GET",
            "protected",
            200,
            token=self.user_token
        )

    def test_admin_route_with_user_token(self):
        """Test admin route with user token (should fail)"""
        success, response = self.run_test(
            "Admin Route with User Token",
            "GET",
            "admin/users",
            403,  # Should be forbidden
            token=self.user_token
        )
        return success  # Success means we got the expected 403 status

    def test_create_location_admin(self):
        """Test creating a location (admin only)"""
        timestamp = datetime.now().strftime('%H%M%S')
        location_data = {
            "name": f"Test Location {timestamp}"
        }
        
        success, response = self.run_test(
            "Create Location (Admin)",
            "POST",
            "locations",
            200,
            data=location_data,
            token=self.admin_token
        )
        if success and 'id' in response:
            self.created_location_id = response['id']
            self.created_location_name = response['name']
            print(f"   Created location: {self.created_location_name} (ID: {self.created_location_id})")
        return success

    # NEW STAGE 2 TESTS
    def test_admin_stats(self):
        """Test admin statistics endpoint"""
        success, response = self.run_test(
            "Admin Statistics",
            "GET",
            "admin/stats",
            200,
            token=self.admin_token
        )
        if success:
            expected_keys = ['total_users', 'pending_users', 'total_locations', 'recent_registrations', 'admin_users', 'regular_users', 'approved_users']
            for key in expected_keys:
                if key not in response:
                    print(f"   ⚠️  Missing key in stats: {key}")
                    return False
            print(f"   Stats: {response['total_users']} users, {response['total_locations']} locations, {response['pending_users']} pending")
        return success

    def test_update_user_role_to_admin(self):
        """Test updating user role to ADMIN"""
        if not self.test_user_id:
            print("❌ No test user ID available for role update")
            return False
            
        return self.run_test(
            "Update User Role to ADMIN",
            "PUT",
            f"admin/users/{self.test_user_id}/role",
            200,
            data={"role": "ADMIN"},
            token=self.admin_token
        )

    def test_update_user_role_to_user(self):
        """Test updating user role back to USER"""
        if not self.test_user_id:
            print("❌ No test user ID available for role update")
            return False
            
        return self.run_test(
            "Update User Role to USER",
            "PUT",
            f"admin/users/{self.test_user_id}/role",
            200,
            data={"role": "USER"},
            token=self.admin_token
        )

    def test_update_user_role_invalid(self):
        """Test updating user role with invalid role (should fail)"""
        if not self.test_user_id:
            print("❌ No test user ID available for role update")
            return False
            
        return self.run_test(
            "Update User Role Invalid",
            "PUT",
            f"admin/users/{self.test_user_id}/role",
            400,  # Should be bad request
            data={"role": "INVALID_ROLE"},
            token=self.admin_token
        )

    def test_update_location(self):
        """Test updating a location"""
        if not hasattr(self, 'created_location_id'):
            print("❌ No created location ID available for update")
            return False
            
        updated_name = f"Updated {self.created_location_name}"
        return self.run_test(
            "Update Location",
            "PUT",
            f"admin/locations/{self.created_location_id}",
            200,
            data={"name": updated_name},
            token=self.admin_token
        )

    def test_delete_user_self_protection(self):
        """Test that admin cannot delete their own account"""
        # First get admin user ID
        success, response = self.run_test(
            "Get Admin User Info",
            "GET",
            "auth/me",
            200,
            token=self.admin_token
        )
        if not success or 'id' not in response:
            print("❌ Could not get admin user ID")
            return False
            
        admin_user_id = response['id']
        
        # Try to delete own account (should fail)
        return self.run_test(
            "Delete Own Account (Should Fail)",
            "DELETE",
            f"admin/users/{admin_user_id}",
            400,  # Should be bad request
            token=self.admin_token,
            expect_json=False
        )

    def test_delete_location_in_use(self):
        """Test deleting a location that's in use (should fail)"""
        if not self.location_id:
            print("❌ No location ID available for deletion test")
            return False
            
        # This should fail because the test user is assigned to this location
        return self.run_test(
            "Delete Location In Use (Should Fail)",
            "DELETE",
            f"admin/locations/{self.location_id}",
            400,  # Should be bad request
            token=self.admin_token,
            expect_json=False
        )

    def test_delete_location_success(self):
        """Test deleting a location that's not in use"""
        if not hasattr(self, 'created_location_id'):
            print("❌ No created location ID available for deletion")
            return False
            
        return self.run_test(
            "Delete Location Success",
            "DELETE",
            f"admin/locations/{self.created_location_id}",
            200,
            token=self.admin_token,
            expect_json=False
        )

    def test_delete_user_success(self):
        """Test deleting a user (should be last test)"""
        if not self.test_user_id:
            print("❌ No test user ID available for deletion")
            return False
            
        return self.run_test(
            "Delete User Success",
            "DELETE",
            f"admin/users/{self.test_user_id}",
            200,
            token=self.admin_token,
            expect_json=False
        )

    def test_get_admin_locations(self):
        """Test getting all locations via admin endpoint"""
        return self.run_test(
            "Get Admin Locations",
            "GET",
            "admin/locations",
            200,
            token=self.admin_token
        )

    def test_unauthorized_access(self):
        """Test accessing protected routes without token"""
        return self.run_test(
            "Unauthorized Access",
            "GET",
            "auth/me",
            401,  # Should be unauthorized
            token=None
        )

def main():
    print("🚀 Starting MonthlyReportsHub API Tests")
    print("=" * 50)
    
    tester = MonthlyReportsHubAPITester()
    
    # Test sequence
    test_sequence = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Get Locations", tester.test_get_locations),
        ("Admin Login", tester.test_admin_login),
        ("Get Current User (Admin)", tester.test_get_current_user_admin),
        ("User Registration", tester.test_user_registration),
        ("User Login Before Approval", tester.test_user_login_before_approval),
        ("Get All Users (Admin)", tester.test_get_all_users_admin),
        ("Approve User", tester.test_approve_user),
        ("User Login After Approval", tester.test_user_login_after_approval),
        ("Get Current User (Regular)", tester.test_get_current_user_regular),
        ("Protected Route", tester.test_protected_route),
        ("Admin Route with User Token", tester.test_admin_route_with_user_token),
        ("Create Location (Admin)", tester.test_create_location_admin),
        ("Unauthorized Access", tester.test_unauthorized_access),
    ]
    
    # Run all tests
    for test_name, test_func in test_sequence:
        try:
            success = test_func()
            if not success:
                print(f"⚠️  Test '{test_name}' failed, but continuing...")
        except Exception as e:
            print(f"💥 Test '{test_name}' crashed: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())