import requests
import sys
import json
from datetime import datetime

class Stage3EnhancedAPITester:
    def __init__(self, base_url="https://dataentry-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.test_user_id = None
        self.location_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_field_ids = []
        self.created_template_id = None
        self.test_report_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, expect_json=True, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=10)

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

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("\n🔐 Setting up authentication...")
        
        # Admin login
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
        else:
            print("❌ Failed to get admin token")
            return False

        # Get locations for user creation
        success, response = self.run_test(
            "Get Locations",
            "GET",
            "locations",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            self.location_id = response[0]['id']
            print(f"   Found location: {response[0]['name']} (ID: {self.location_id})")
        else:
            print("❌ Failed to get locations")
            return False

        # Create and approve test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "username": f"stage3user_{timestamp}",
            "email": f"stage3user_{timestamp}@example.com",
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
        else:
            print("❌ Failed to register user")
            return False

        # Approve user
        success, response = self.run_test(
            "Approve User",
            "PUT",
            f"admin/users/{self.test_user_id}/approve",
            200,
            token=self.admin_token
        )
        if not success:
            print("❌ Failed to approve user")
            return False

        # User login
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"username": self.test_username, "password": self.test_password}
        )
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            print(f"   User token obtained: {self.user_token[:20]}...")
        else:
            print("❌ Failed to get user token")
            return False

        return True

    # STAGE 3 ENHANCED TESTS - Dynamic Field Management
    def test_get_dynamic_fields(self):
        """Test getting all dynamic fields"""
        return self.run_test(
            "Get Dynamic Fields",
            "GET",
            "admin/dynamic-fields",
            200,
            token=self.admin_token
        )

    def test_get_dynamic_fields_with_deleted(self):
        """Test getting dynamic fields including deleted ones"""
        return self.run_test(
            "Get Dynamic Fields (Include Deleted)",
            "GET",
            "admin/dynamic-fields",
            200,
            token=self.admin_token,
            params={"include_deleted": True}
        )

    def test_get_field_sections(self):
        """Test getting field sections"""
        return self.run_test(
            "Get Field Sections",
            "GET",
            "admin/dynamic-fields/sections",
            200,
            token=self.admin_token
        )

    def test_create_text_field(self):
        """Test creating a text dynamic field"""
        field_data = {
            "section": "Test Section",
            "label": "Test Text Field",
            "field_type": "text",
            "placeholder": "Enter text here",
            "help_text": "This is a test text field"
        }
        
        success, response = self.run_test(
            "Create Text Dynamic Field",
            "POST",
            "admin/dynamic-fields",
            200,
            data=field_data,
            token=self.admin_token
        )
        if success and 'id' in response:
            self.created_field_ids.append(response['id'])
            print(f"   Created text field ID: {response['id']}")
        return success

    def test_create_dropdown_field(self):
        """Test creating a dropdown dynamic field"""
        field_data = {
            "section": "Test Section",
            "label": "Test Dropdown Field",
            "field_type": "dropdown",
            "choices": ["Option 1", "Option 2", "Option 3"],
            "help_text": "Select one option"
        }
        
        success, response = self.run_test(
            "Create Dropdown Dynamic Field",
            "POST",
            "admin/dynamic-fields",
            200,
            data=field_data,
            token=self.admin_token
        )
        if success and 'id' in response:
            self.created_field_ids.append(response['id'])
            print(f"   Created dropdown field ID: {response['id']}")
        return success

    def test_create_number_field(self):
        """Test creating a number dynamic field"""
        field_data = {
            "section": "Test Section",
            "label": "Test Number Field",
            "field_type": "number",
            "placeholder": "Enter number",
            "validation": {"min": 0, "max": 100},
            "help_text": "Enter a number between 0 and 100"
        }
        
        success, response = self.run_test(
            "Create Number Dynamic Field",
            "POST",
            "admin/dynamic-fields",
            200,
            data=field_data,
            token=self.admin_token
        )
        if success and 'id' in response:
            self.created_field_ids.append(response['id'])
            print(f"   Created number field ID: {response['id']}")
        return success

    def test_create_multiselect_field(self):
        """Test creating a multiselect dynamic field"""
        field_data = {
            "section": "Test Section",
            "label": "Test Multiselect Field",
            "field_type": "multiselect",
            "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
            "help_text": "Select multiple options"
        }
        
        success, response = self.run_test(
            "Create Multiselect Dynamic Field",
            "POST",
            "admin/dynamic-fields",
            200,
            data=field_data,
            token=self.admin_token
        )
        if success and 'id' in response:
            self.created_field_ids.append(response['id'])
            print(f"   Created multiselect field ID: {response['id']}")
        return success

    def test_create_invalid_field_type(self):
        """Test creating field with invalid type (should fail)"""
        field_data = {
            "section": "Test Section",
            "label": "Invalid Field",
            "field_type": "invalid_type",
            "help_text": "This should fail"
        }
        
        return self.run_test(
            "Create Invalid Field Type",
            "POST",
            "admin/dynamic-fields",
            400,
            data=field_data,
            token=self.admin_token
        )

    def test_create_dropdown_without_choices(self):
        """Test creating dropdown without choices (should fail)"""
        field_data = {
            "section": "Test Section",
            "label": "Dropdown Without Choices",
            "field_type": "dropdown",
            "help_text": "This should fail"
        }
        
        return self.run_test(
            "Create Dropdown Without Choices",
            "POST",
            "admin/dynamic-fields",
            400,
            data=field_data,
            token=self.admin_token
        )

    def test_update_dynamic_field(self):
        """Test updating a dynamic field"""
        if not self.created_field_ids:
            print("❌ No created field IDs available for update")
            return False
            
        field_id = self.created_field_ids[0]
        update_data = {
            "label": "Updated Test Field",
            "help_text": "This field has been updated"
        }
        
        return self.run_test(
            "Update Dynamic Field",
            "PUT",
            f"admin/dynamic-fields/{field_id}",
            200,
            data=update_data,
            token=self.admin_token
        )

    def test_soft_delete_dynamic_field(self):
        """Test soft deleting a dynamic field"""
        if len(self.created_field_ids) < 2:
            print("❌ Not enough created field IDs available for deletion")
            return False
            
        field_id = self.created_field_ids[1]
        return self.run_test(
            "Soft Delete Dynamic Field",
            "DELETE",
            f"admin/dynamic-fields/{field_id}",
            200,
            token=self.admin_token
        )

    def test_restore_dynamic_field(self):
        """Test restoring a soft-deleted dynamic field"""
        if len(self.created_field_ids) < 2:
            print("❌ Not enough created field IDs available for restoration")
            return False
            
        field_id = self.created_field_ids[1]  # The one we just deleted
        return self.run_test(
            "Restore Dynamic Field",
            "POST",
            f"admin/dynamic-fields/{field_id}/restore",
            200,
            token=self.admin_token
        )

    # STAGE 3 ENHANCED TESTS - Enhanced Template Builder
    def test_get_supported_field_types(self):
        """Test getting supported field types"""
        return self.run_test(
            "Get Supported Field Types",
            "GET",
            "admin/field-types",
            200,
            token=self.admin_token
        )

    def test_create_template_from_dynamic_fields(self):
        """Test creating template from dynamic fields"""
        if len(self.created_field_ids) < 3:
            print("❌ Not enough created field IDs available for template creation")
            return False
            
        # Use first 3 created fields
        field_ids = self.created_field_ids[:3]
        
        success, response = self.run_test(
            "Create Template from Dynamic Fields",
            "POST",
            "admin/report-templates/from-fields",
            200,
            token=self.admin_token,
            params={
                "template_name": "Stage 3 Test Template",
                "template_description": "Template created from dynamic fields for testing",
                "field_ids": field_ids,
                "template_category": "Testing"
            }
        )
        if success and 'id' in response:
            self.created_template_id = response['id']
            print(f"   Created template ID: {self.created_template_id}")
        return success

    def test_preview_template(self):
        """Test template preview functionality"""
        template_data = {
            "name": "Preview Test Template",
            "description": "This is a template preview test",
            "fields": [
                {
                    "label": "Sample Text Field",
                    "field_type": "text",
                    "placeholder": "Enter text",
                    "required": True
                },
                {
                    "label": "Sample Dropdown",
                    "field_type": "dropdown",
                    "options": ["Option 1", "Option 2"],
                    "required": False
                }
            ]
        }
        
        return self.run_test(
            "Preview Template",
            "POST",
            "admin/report-templates/preview",
            200,
            data=template_data,
            token=self.admin_token
        )

    # STAGE 3 ENHANCED TESTS - Enhanced Analytics
    def test_enhanced_analytics(self):
        """Test enhanced analytics endpoint"""
        success, response = self.run_test(
            "Enhanced Analytics",
            "GET",
            "admin/analytics",
            200,
            token=self.admin_token
        )
        
        if success:
            # Verify all expected analytics fields are present
            expected_fields = [
                'total_users', 'approved_users', 'pending_users', 'admin_users', 'regular_users',
                'total_locations', 'total_templates', 'total_fields', 'total_reports',
                'submitted_reports', 'draft_reports', 'recent_registrations', 'recent_submissions',
                'monthly_submissions', 'field_sections', 'section_stats', 'approval_rate', 'submission_rate'
            ]
            
            missing_fields = []
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️  Missing analytics fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All analytics fields present")
                print(f"   Analytics summary: {response['total_users']} users, {response['total_fields']} fields, {response['total_reports']} reports")
        
        return success

    # STAGE 3 ENHANCED TESTS - Advanced Report Management
    def setup_test_reports(self):
        """Create some test reports for advanced management testing"""
        print("\n📊 Setting up test reports...")
        
        # Get a template to use
        success, response = self.run_test(
            "Get Templates for Report Setup",
            "GET",
            "admin/report-templates",
            200,
            token=self.admin_token
        )
        
        if not success or not response:
            print("❌ Failed to get templates for report setup")
            return False
            
        template_id = response[0]['id'] if response else None
        if not template_id:
            print("❌ No template available for report setup")
            return False

        # Create multiple test reports with different statuses
        test_reports = [
            {
                "template_id": template_id,
                "report_period": "2025-01",
                "status": "draft",
                "data": {"test_field": "Draft report data"}
            },
            {
                "template_id": template_id,
                "report_period": "2025-02",
                "status": "submitted",
                "data": {"test_field": "Submitted report data"}
            }
        ]
        
        for i, report_data in enumerate(test_reports):
            success, response = self.run_test(
                f"Create Test Report {i+1}",
                "POST",
                "reports",
                200,
                data=report_data,
                token=self.user_token
            )
            if success and 'id' in response:
                self.test_report_ids.append(response['id'])
                print(f"   Created test report ID: {response['id']}")
        
        return len(self.test_report_ids) > 0

    def test_search_reports_basic(self):
        """Test basic report search"""
        return self.run_test(
            "Search Reports (Basic)",
            "GET",
            "admin/reports/search",
            200,
            token=self.admin_token
        )

    def test_search_reports_with_filters(self):
        """Test report search with various filters"""
        # Test with status filter
        success1, response1 = self.run_test(
            "Search Reports (Status Filter)",
            "GET",
            "admin/reports/search",
            200,
            token=self.admin_token,
            params={"status": "submitted"}
        )
        
        # Test with pagination
        success2, response2 = self.run_test(
            "Search Reports (Pagination)",
            "GET",
            "admin/reports/search",
            200,
            token=self.admin_token,
            params={"page": 1, "limit": 5}
        )
        
        # Test with user filter
        success3, response3 = self.run_test(
            "Search Reports (User Filter)",
            "GET",
            "admin/reports/search",
            200,
            token=self.admin_token,
            params={"user_id": self.test_user_id}
        )
        
        return success1 and success2 and success3

    def test_bulk_report_actions_approve(self):
        """Test bulk approve action on reports"""
        if not self.test_report_ids:
            print("❌ No test report IDs available for bulk actions")
            return False
            
        return self.run_test(
            "Bulk Approve Reports",
            "POST",
            "admin/reports/bulk-actions",
            200,
            data={
                "action": "approve",
                "report_ids": self.test_report_ids[:1]  # Use first report
            },
            token=self.admin_token
        )

    def test_bulk_report_actions_reject(self):
        """Test bulk reject action on reports"""
        if len(self.test_report_ids) < 2:
            print("❌ Not enough test report IDs available for bulk reject")
            return False
            
        return self.run_test(
            "Bulk Reject Reports",
            "POST",
            "admin/reports/bulk-actions",
            200,
            data={
                "action": "reject",
                "report_ids": self.test_report_ids[1:2]  # Use second report
            },
            token=self.admin_token
        )

    def test_bulk_report_actions_mark_reviewed(self):
        """Test bulk mark reviewed action on reports"""
        if not self.test_report_ids:
            print("❌ No test report IDs available for bulk mark reviewed")
            return False
            
        return self.run_test(
            "Bulk Mark Reviewed Reports",
            "POST",
            "admin/reports/bulk-actions",
            200,
            data={
                "action": "mark_reviewed",
                "report_ids": self.test_report_ids
            },
            token=self.admin_token
        )

    def test_bulk_report_actions_invalid(self):
        """Test bulk action with invalid action (should fail)"""
        if not self.test_report_ids:
            print("❌ No test report IDs available for invalid bulk action test")
            return False
            
        return self.run_test(
            "Bulk Invalid Action",
            "POST",
            "admin/reports/bulk-actions",
            400,
            data={
                "action": "invalid_action",
                "report_ids": self.test_report_ids[:1]
            },
            token=self.admin_token
        )

    def test_export_reports_csv(self):
        """Test exporting reports in CSV format"""
        return self.run_test(
            "Export Reports (CSV)",
            "GET",
            "admin/reports/export",
            200,
            token=self.admin_token,
            params={"format": "csv"}
        )

    def test_export_reports_json(self):
        """Test exporting reports in JSON format"""
        return self.run_test(
            "Export Reports (JSON)",
            "GET",
            "admin/reports/export",
            200,
            token=self.admin_token,
            params={"format": "json"}
        )

    def test_export_reports_with_filters(self):
        """Test exporting reports with filters"""
        return self.run_test(
            "Export Reports (With Filters)",
            "GET",
            "admin/reports/export",
            200,
            token=self.admin_token,
            params={
                "format": "csv",
                "status": "submitted",
                "user_id": self.test_user_id
            }
        )

    # Authorization Tests
    def test_dynamic_fields_user_access(self):
        """Test that regular users cannot access dynamic fields endpoints"""
        return self.run_test(
            "Dynamic Fields (User Access - Should Fail)",
            "GET",
            "admin/dynamic-fields",
            403,
            token=self.user_token
        )

    def test_analytics_user_access(self):
        """Test that regular users cannot access analytics endpoint"""
        return self.run_test(
            "Analytics (User Access - Should Fail)",
            "GET",
            "admin/analytics",
            403,
            token=self.user_token
        )

    def test_bulk_actions_user_access(self):
        """Test that regular users cannot perform bulk actions"""
        return self.run_test(
            "Bulk Actions (User Access - Should Fail)",
            "POST",
            "admin/reports/bulk-actions",
            403,
            data={"action": "approve", "report_ids": []},
            token=self.user_token
        )

def main():
    print("🚀 Starting Stage 3 Enhanced MonthlyReportsHub API Tests")
    print("=" * 70)
    
    tester = Stage3EnhancedAPITester()
    
    # Setup authentication first
    if not tester.setup_authentication():
        print("❌ Failed to setup authentication. Exiting.")
        return 1
    
    # Test sequence for Stage 3 enhanced features
    test_sequence = [
        # Dynamic Field Management Tests
        ("Get Dynamic Fields", tester.test_get_dynamic_fields),
        ("Get Dynamic Fields (Include Deleted)", tester.test_get_dynamic_fields_with_deleted),
        ("Get Field Sections", tester.test_get_field_sections),
        ("Create Text Dynamic Field", tester.test_create_text_field),
        ("Create Dropdown Dynamic Field", tester.test_create_dropdown_field),
        ("Create Number Dynamic Field", tester.test_create_number_field),
        ("Create Multiselect Dynamic Field", tester.test_create_multiselect_field),
        ("Create Invalid Field Type", tester.test_create_invalid_field_type),
        ("Create Dropdown Without Choices", tester.test_create_dropdown_without_choices),
        ("Update Dynamic Field", tester.test_update_dynamic_field),
        ("Soft Delete Dynamic Field", tester.test_soft_delete_dynamic_field),
        ("Restore Dynamic Field", tester.test_restore_dynamic_field),
        
        # Enhanced Template Builder Tests
        ("Get Supported Field Types", tester.test_get_supported_field_types),
        ("Create Template from Dynamic Fields", tester.test_create_template_from_dynamic_fields),
        ("Preview Template", tester.test_preview_template),
        
        # Enhanced Analytics Tests
        ("Enhanced Analytics", tester.test_enhanced_analytics),
        
        # Advanced Report Management Tests (Setup)
        ("Setup Test Reports", tester.setup_test_reports),
        ("Search Reports (Basic)", tester.test_search_reports_basic),
        ("Search Reports (With Filters)", tester.test_search_reports_with_filters),
        ("Bulk Approve Reports", tester.test_bulk_report_actions_approve),
        ("Bulk Reject Reports", tester.test_bulk_report_actions_reject),
        ("Bulk Mark Reviewed Reports", tester.test_bulk_report_actions_mark_reviewed),
        ("Bulk Invalid Action", tester.test_bulk_report_actions_invalid),
        ("Export Reports (CSV)", tester.test_export_reports_csv),
        ("Export Reports (JSON)", tester.test_export_reports_json),
        ("Export Reports (With Filters)", tester.test_export_reports_with_filters),
        
        # Authorization Tests
        ("Dynamic Fields (User Access - Should Fail)", tester.test_dynamic_fields_user_access),
        ("Analytics (User Access - Should Fail)", tester.test_analytics_user_access),
        ("Bulk Actions (User Access - Should Fail)", tester.test_bulk_actions_user_access),
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
    print("\n" + "=" * 70)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Stage 3 enhanced features working correctly!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())