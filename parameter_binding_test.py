import requests
import sys
import json
from datetime import datetime

class ParameterBindingTester:
    def __init__(self, base_url="https://model-definition-add.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.field_ids = []
        self.report_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, expect_json=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if expect_json:
                    try:
                        response_data = response.json()
                        print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
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

    def test_admin_login(self):
        """Test admin login to get token"""
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

    def test_get_dynamic_fields(self):
        """Get dynamic fields to use their IDs in template creation"""
        success, response = self.run_test(
            "Get Dynamic Fields",
            "GET",
            "admin/dynamic-fields",
            200,
            token=self.admin_token
        )
        if success and isinstance(response, list) and len(response) > 0:
            # Get first few field IDs
            self.field_ids = [field['id'] for field in response[:3]]
            print(f"   Found {len(self.field_ids)} field IDs: {self.field_ids}")
            return True
        return success

    def test_create_user_and_reports(self):
        """Create a test user and reports for bulk actions"""
        # First register a test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "TestPass123!",
            "location_id": None
        }
        
        success, response = self.run_test(
            "Register Test User",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        if not success:
            return False
            
        test_user_id = response['id']
        
        # Approve the user
        success, response = self.run_test(
            "Approve Test User",
            "PUT",
            f"admin/users/{test_user_id}/approve",
            200,
            token=self.admin_token
        )
        if not success:
            return False
        
        # Login as the test user
        success, response = self.run_test(
            "Test User Login",
            "POST",
            "auth/login",
            200,
            data={"username": test_user_data["username"], "password": test_user_data["password"]}
        )
        if not success:
            return False
            
        user_token = response['access_token']
        
        # Get available templates
        success, response = self.run_test(
            "Get Templates for Reports",
            "GET",
            "report-templates",
            200,
            token=user_token
        )
        if not success or not response:
            return False
            
        template_id = response[0]['id']
        
        # Create two test reports
        current_month = datetime.now().strftime('%Y-%m')
        next_month = datetime.now().replace(day=1)
        if next_month.month == 12:
            next_month = next_month.replace(year=next_month.year + 1, month=1)
        else:
            next_month = next_month.replace(month=next_month.month + 1)
        next_month_str = next_month.strftime('%Y-%m')
        
        # Create first report
        report_data_1 = {
            "template_id": template_id,
            "report_period": current_month,
            "status": "submitted",
            "data": {
                "key_achievements": "Test achievements for bulk action testing",
                "challenges": "Test challenges",
                "goals_next_month": "Test goals",
                "satisfaction_rating": "Satisfied",
                "hours_worked": 160
            }
        }
        
        success, response = self.run_test(
            "Create Test Report 1",
            "POST",
            "reports",
            200,
            data=report_data_1,
            token=user_token
        )
        if success:
            self.report_ids.append(response['id'])
        
        # Create second report
        report_data_2 = {
            "template_id": template_id,
            "report_period": next_month_str,
            "status": "submitted",
            "data": {
                "key_achievements": "Second test achievements for bulk action testing",
                "challenges": "Second test challenges",
                "goals_next_month": "Second test goals",
                "satisfaction_rating": "Very Satisfied",
                "hours_worked": 170
            }
        }
        
        success, response = self.run_test(
            "Create Test Report 2",
            "POST",
            "reports",
            200,
            data=report_data_2,
            token=user_token
        )
        if success:
            self.report_ids.append(response['id'])
        
        print(f"   Created {len(self.report_ids)} reports for bulk testing: {self.report_ids}")
        return len(self.report_ids) >= 2

    def test_template_from_fields_success(self):
        """Test POST /admin/report-templates/from-fields with valid data"""
        if not self.field_ids:
            print("❌ No field IDs available for template creation")
            return False

        template_data = {
            "template_name": "Test Template from Fields",
            "template_description": "A test template created from dynamic fields",
            "field_ids": self.field_ids,
            "template_category": "Test"
        }

        success, response = self.run_test(
            "Create Template from Fields - Success",
            "POST",
            "admin/report-templates/from-fields",
            200,
            data=template_data,
            token=self.admin_token
        )
        
        if success and 'id' in response:
            self.created_template_id = response['id']
            print(f"   Created template ID: {self.created_template_id}")
        
        return success

    def test_template_from_fields_validation_error(self):
        """Test POST /admin/report-templates/from-fields with invalid data"""
        # Test with missing required fields
        invalid_data = {
            "template_name": "",  # Empty name should fail
            "template_description": "Test description",
            "field_ids": [],  # Empty field_ids should fail
            "template_category": "Test"
        }

        success, response = self.run_test(
            "Create Template from Fields - Validation Error",
            "POST",
            "admin/report-templates/from-fields",
            400,  # Expecting validation error
            data=invalid_data,
            token=self.admin_token
        )
        
        return success

    def test_template_from_fields_duplicate_name(self):
        """Test POST /admin/report-templates/from-fields with duplicate name"""
        if not self.field_ids:
            print("❌ No field IDs available for template creation")
            return False

        # Try to create template with same name as before
        duplicate_data = {
            "template_name": "Test Template from Fields",  # Same name as previous test
            "template_description": "Another test template",
            "field_ids": self.field_ids,
            "template_category": "Test"
        }

        success, response = self.run_test(
            "Create Template from Fields - Duplicate Name",
            "POST",
            "admin/report-templates/from-fields",
            400,  # Expecting duplicate name error
            data=duplicate_data,
            token=self.admin_token
        )
        
        return success

    def test_bulk_actions_mark_reviewed(self):
        """Test POST /admin/reports/bulk-actions with mark_reviewed action"""
        if not self.report_ids:
            print("❌ No report IDs available for bulk action")
            return False

        bulk_data = {
            "action": "mark_reviewed",
            "report_ids": self.report_ids
        }

        success, response = self.run_test(
            "Bulk Actions - Mark Reviewed",
            "POST",
            "admin/reports/bulk-actions",
            200,
            data=bulk_data,
            token=self.admin_token
        )
        
        return success

    def test_bulk_actions_approve(self):
        """Test POST /admin/reports/bulk-actions with approve action"""
        if not self.report_ids:
            print("❌ No report IDs available for bulk action")
            return False

        bulk_data = {
            "action": "approve",
            "report_ids": self.report_ids
        }

        success, response = self.run_test(
            "Bulk Actions - Approve",
            "POST",
            "admin/reports/bulk-actions",
            200,
            data=bulk_data,
            token=self.admin_token
        )
        
        return success

    def test_bulk_actions_invalid_action(self):
        """Test POST /admin/reports/bulk-actions with invalid action"""
        if not self.report_ids:
            print("❌ No report IDs available for bulk action")
            return False

        invalid_data = {
            "action": "invalid_action",
            "report_ids": self.report_ids
        }

        success, response = self.run_test(
            "Bulk Actions - Invalid Action",
            "POST",
            "admin/reports/bulk-actions",
            400,  # Expecting validation error
            data=invalid_data,
            token=self.admin_token
        )
        
        return success

    def test_bulk_actions_empty_report_ids(self):
        """Test POST /admin/reports/bulk-actions with empty report_ids"""
        empty_data = {
            "action": "mark_reviewed",
            "report_ids": []
        }

        success, response = self.run_test(
            "Bulk Actions - Empty Report IDs",
            "POST",
            "admin/reports/bulk-actions",
            400,  # Expecting validation error
            data=empty_data,
            token=self.admin_token
        )
        
        return success

    def test_bulk_actions_nonexistent_report_ids(self):
        """Test POST /admin/reports/bulk-actions with non-existent report IDs"""
        nonexistent_data = {
            "action": "mark_reviewed",
            "report_ids": ["nonexistent-id-1", "nonexistent-id-2"]
        }

        success, response = self.run_test(
            "Bulk Actions - Non-existent Report IDs",
            "POST",
            "admin/reports/bulk-actions",
            400,  # Expecting validation error
            data=nonexistent_data,
            token=self.admin_token
        )
        
        return success

def main():
    print("🚀 Starting Parameter Binding Tests for Fixed Endpoints")
    print("=" * 60)
    
    tester = ParameterBindingTester()
    
    # Test sequence focusing on the two problematic endpoints
    test_sequence = [
        # Setup
        ("Admin Login", tester.test_admin_login),
        ("Get Dynamic Fields", tester.test_get_dynamic_fields),
        ("Get Reports for Bulk Action", tester.test_get_reports_for_bulk_action),
        
        # Template from Fields Tests
        ("Template from Fields - Success", tester.test_template_from_fields_success),
        ("Template from Fields - Validation Error", tester.test_template_from_fields_validation_error),
        ("Template from Fields - Duplicate Name", tester.test_template_from_fields_duplicate_name),
        
        # Bulk Actions Tests
        ("Bulk Actions - Mark Reviewed", tester.test_bulk_actions_mark_reviewed),
        ("Bulk Actions - Approve", tester.test_bulk_actions_approve),
        ("Bulk Actions - Invalid Action", tester.test_bulk_actions_invalid_action),
        ("Bulk Actions - Empty Report IDs", tester.test_bulk_actions_empty_report_ids),
        ("Bulk Actions - Non-existent Report IDs", tester.test_bulk_actions_nonexistent_report_ids),
    ]
    
    # Run all tests
    failed_tests = []
    for test_name, test_func in test_sequence:
        try:
            success = test_func()
            if not success:
                failed_tests.append(test_name)
                print(f"⚠️  Test '{test_name}' failed, but continuing...")
        except Exception as e:
            failed_tests.append(test_name)
            print(f"💥 Test '{test_name}' crashed: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All parameter binding tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())