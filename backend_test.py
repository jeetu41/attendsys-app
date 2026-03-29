#!/usr/bin/env python3
"""
AttendSys Backend API Testing Script
Tests all the critical backend APIs as specified in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://absence-alert-4.preview.emergentagent.com/api"

class AttendSysAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.tokens = {}
        self.test_data = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_health_check(self):
        """Test 1: Health check endpoint"""
        self.log("Testing health check endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health check passed: {data}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            return False
    
    def register_platform_admin(self):
        """Test 2: Register platform admin (first user)"""
        self.log("Registering platform admin...")
        try:
            payload = {
                "email": "admin@test.com",
                "password": "admin123",
                "name": "Platform Admin",
                "role": "platform_admin"
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['admin'] = data['token']
                self.test_data['admin_id'] = data['user']['id']
                self.log(f"✅ Platform admin registered successfully")
                return True
            else:
                self.log(f"❌ Platform admin registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Platform admin registration error: {str(e)}", "ERROR")
            return False
    
    def login_platform_admin(self):
        """Test 3: Login as platform admin"""
        self.log("Logging in as platform admin...")
        try:
            payload = {
                "email": "admin@test.com",
                "password": "admin123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['admin'] = data['token']
                self.log(f"✅ Platform admin login successful")
                return True
            else:
                self.log(f"❌ Platform admin login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Platform admin login error: {str(e)}", "ERROR")
            return False
    
    def create_school(self):
        """Test 4: Create a school"""
        self.log("Creating a school...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            payload = {
                "name": "Test School",
                "address": "123 Main St",
                "contact_email": "school@test.com",
                "contact_phone": "1234567890"
            }
            response = self.session.post(f"{self.base_url}/admin/schools", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['school_cnn'] = data['cnn_token']
                self.test_data['school_id'] = data['_id']
                self.log(f"✅ School created successfully. CNN Token: {data['cnn_token']}")
                return True
            else:
                self.log(f"❌ School creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ School creation error: {str(e)}", "ERROR")
            return False
    
    def register_teacher(self):
        """Test 5: Register teacher with CNN"""
        self.log("Registering teacher with CNN...")
        try:
            payload = {
                "email": "teacher@test.com",
                "password": "teacher123",
                "name": "Test Teacher",
                "role": "teacher",
                "school_cnn": self.test_data['school_cnn']
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.test_data['teacher_id'] = data['user']['id']
                self.log(f"✅ Teacher registered successfully")
                return True
            else:
                self.log(f"❌ Teacher registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Teacher registration error: {str(e)}", "ERROR")
            return False
    
    def approve_teacher(self):
        """Test 6: Approve teacher"""
        self.log("Approving teacher...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            payload = {
                "teacher_id": self.test_data['teacher_id'],
                "approved": True
            }
            response = self.session.post(f"{self.base_url}/admin/teachers/approve", json=payload, headers=headers)
            if response.status_code == 200:
                self.log(f"✅ Teacher approved successfully")
                return True
            else:
                self.log(f"❌ Teacher approval failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Teacher approval error: {str(e)}", "ERROR")
            return False
    
    def login_teacher(self):
        """Test 7: Login as teacher"""
        self.log("Logging in as teacher...")
        try:
            payload = {
                "email": "teacher@test.com",
                "password": "teacher123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['teacher'] = data['token']
                self.log(f"✅ Teacher login successful")
                return True
            else:
                self.log(f"❌ Teacher login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Teacher login error: {str(e)}", "ERROR")
            return False
    
    def add_student(self):
        """Test 8: Add a student"""
        self.log("Adding a student...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            payload = {
                "name": "John Doe",
                "roll_number": "101",
                "class_name": "5A",
                "parent_phone": "9876543210"
            }
            response = self.session.post(f"{self.base_url}/teacher/students", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['student_id'] = data['_id']
                self.log(f"✅ Student added successfully")
                return True
            else:
                self.log(f"❌ Student addition failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Student addition error: {str(e)}", "ERROR")
            return False
    
    def request_otp_for_parent(self):
        """Test 9: Request OTP for parent (with CNN + Roll)"""
        self.log("Requesting OTP for parent...")
        try:
            payload = {
                "school_cnn": self.test_data['school_cnn'],
                "roll_number": "101"
            }
            response = self.session.post(f"{self.base_url}/parent/request-otp", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.test_data['otp_code'] = data['otp']  # In development, OTP is returned
                self.log(f"✅ OTP requested successfully. OTP: {data['otp']}")
                return True
            else:
                self.log(f"❌ OTP request failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ OTP request error: {str(e)}", "ERROR")
            return False
    
    def test_otp_validation_fix(self):
        """Test: Verify OTP request requires BOTH school_cnn and roll_number"""
        self.log("Testing OTP validation fix - testing with only roll_number...")
        try:
            # Test with only roll_number (should fail)
            payload = {
                "roll_number": "101"
            }
            response = self.session.post(f"{self.base_url}/parent/request-otp", json=payload)
            if response.status_code == 422:  # Validation error expected
                self.log(f"✅ OTP validation fix working - requires both school_cnn and roll_number")
                return True
            else:
                self.log(f"❌ OTP validation fix not working - should require both fields: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ OTP validation test error: {str(e)}", "ERROR")
            return False
    
    def register_parent_with_otp(self):
        """Test 10: Register parent with OTP"""
        self.log("Registering parent with OTP...")
        try:
            payload = {
                "email": "parent@test.com",
                "password": "parent123",
                "name": "Parent Name",
                "role": "parent",
                "school_cnn": self.test_data['school_cnn'],
                "student_roll": "101",
                "otp_code": self.test_data['otp_code']
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['parent'] = data['token']
                self.test_data['parent_id'] = data['user']['id']
                self.log(f"✅ Parent registered successfully")
                return True
            else:
                self.log(f"❌ Parent registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Parent registration error: {str(e)}", "ERROR")
            return False
    
    def mark_attendance(self):
        """Test 11: Mark attendance"""
        self.log("Marking attendance...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            payload = {
                "records": [{
                    "student_id": self.test_data['student_id'],
                    "date": "2025-03-29",
                    "status": "present"
                }]
            }
            response = self.session.post(f"{self.base_url}/teacher/attendance", json=payload, headers=headers)
            if response.status_code == 200:
                self.log(f"✅ Attendance marked successfully")
                return True
            else:
                self.log(f"❌ Attendance marking failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Attendance marking error: {str(e)}", "ERROR")
            return False
    
    def get_students_as_teacher(self):
        """Test 12: Get students as teacher"""
        self.log("Getting students as teacher...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            response = self.session.get(f"{self.base_url}/teacher/students", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Retrieved {len(data)} students as teacher")
                return True
            else:
                self.log(f"❌ Getting students as teacher failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting students as teacher error: {str(e)}", "ERROR")
            return False
    
    def login_parent(self):
        """Login as parent before getting children"""
        self.log("Logging in as parent...")
        try:
            payload = {
                "email": "parent@test.com",
                "password": "parent123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['parent'] = data['token']
                self.log(f"✅ Parent login successful")
                return True
            else:
                self.log(f"❌ Parent login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Parent login error: {str(e)}", "ERROR")
            return False
    
    def get_children_as_parent(self):
        """Test 13: Get children as parent"""
        self.log("Getting children as parent...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['parent']}"}
            response = self.session.get(f"{self.base_url}/parent/children", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Retrieved {len(data)} children as parent")
                return True
            else:
                self.log(f"❌ Getting children as parent failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting children as parent error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("Starting AttendSys Backend API Tests...")
        self.log(f"Backend URL: {self.base_url}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Register Platform Admin", self.register_platform_admin),
            ("Login Platform Admin", self.login_platform_admin),
            ("Create School", self.create_school),
            ("Register Teacher", self.register_teacher),
            ("Approve Teacher", self.approve_teacher),
            ("Login Teacher", self.login_teacher),
            ("Add Student", self.add_student),
            ("Request OTP for Parent", self.request_otp_for_parent),
            ("Test OTP Validation Fix", self.test_otp_validation_fix),
            ("Register Parent with OTP", self.register_parent_with_otp),
            ("Mark Attendance", self.mark_attendance),
            ("Get Students as Teacher", self.get_students_as_teacher),
            ("Login Parent", self.login_parent),
            ("Get Children as Parent", self.get_children_as_parent)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ {test_name} crashed: {str(e)}", "ERROR")
                failed += 1
        
        self.log(f"\n=== TEST SUMMARY ===")
        self.log(f"✅ Passed: {passed}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"Total: {passed + failed}")
        
        if failed == 0:
            self.log("🎉 All tests passed!")
            return True
        else:
            self.log(f"⚠️  {failed} test(s) failed")
            return False

if __name__ == "__main__":
    tester = AttendSysAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)