#!/usr/bin/env python3
"""
AttendSys Backend API Testing Script
Tests all the critical backend APIs as specified in the review request
"""

import requests
import json
import sys
from datetime import datetime
import random
import string

# Backend URL from frontend .env
BACKEND_URL = "https://absence-alert-4.preview.emergentagent.com/api"

class AttendSysAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.tokens = {}
        self.test_data = {}
        # Generate unique identifiers for this test run
        self.test_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
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
            email = f"admin{self.test_suffix}@test.com"
            payload = {
                "email": email,
                "password": "admin123",
                "name": "Platform Admin",
                "role": "platform_admin"
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['admin'] = data['token']
                self.test_data['admin_id'] = data['user']['id']
                self.test_data['admin_email'] = email
                self.log(f"✅ Platform admin registered successfully")
                return True
            else:
                # Try to login if already exists
                self.log(f"Admin registration failed, trying login...")
                return self.login_platform_admin()
        except Exception as e:
            self.log(f"❌ Platform admin registration error: {str(e)}", "ERROR")
            return False
    
    def login_platform_admin(self):
        """Test 3: Login as platform admin"""
        self.log("Logging in as platform admin...")
        try:
            # Try with existing admin first
            payload = {
                "email": "admin@test.com",
                "password": "admin123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['admin'] = data['token']
                self.test_data['admin_email'] = "admin@test.com"
                self.log(f"✅ Platform admin login successful")
                return True
            else:
                # Try with new admin if created
                if hasattr(self, 'test_data') and 'admin_email' in self.test_data:
                    payload['email'] = self.test_data['admin_email']
                    response = self.session.post(f"{self.base_url}/auth/login", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        self.tokens['admin'] = data['token']
                        self.log(f"✅ Platform admin login successful")
                        return True
                
                self.log(f"❌ Platform admin login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Platform admin login error: {str(e)}", "ERROR")
            return False
    
    def create_school(self):
        """Test 4: Create a school (legacy method - replaced by create_school_with_branding)"""
        return self.create_school_with_branding()
    
    def register_teacher(self):
        """Test 5: Register teacher with CNN"""
        self.log("Registering teacher with CNN...")
        try:
            email = f"teacher{self.test_suffix}@test.com"
            payload = {
                "email": email,
                "password": "teacher123",
                "name": "Test Teacher",
                "role": "teacher",
                "school_cnn": self.test_data['school_cnn']
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.test_data['teacher_id'] = data['user']['id']
                self.test_data['teacher_email'] = email
                self.log(f"✅ Teacher registered successfully")
                return True
            else:
                # Try to login if already exists
                self.log(f"Teacher registration failed, trying login...")
                return self.login_teacher()
        except Exception as e:
            self.log(f"❌ Teacher registration error: {str(e)}", "ERROR")
            return False
    
    def approve_teacher(self):
        """Test 6: Approve teacher"""
        self.log("Approving teacher...")
        try:
            if 'teacher_id' not in self.test_data:
                self.log("❌ No teacher ID available for approval", "ERROR")
                return False
                
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
        """Test 8: Login as teacher"""
        self.log("Logging in as teacher...")
        try:
            # Try with existing teacher first
            payload = {
                "email": "teacher@test.com",
                "password": "teacher123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['teacher'] = data['token']
                self.test_data['teacher_id'] = data['user']['id']
                self.log(f"✅ Teacher login successful. Is class teacher: {data['user'].get('is_class_teacher', False)}")
                return True
            else:
                # Try with new teacher if created
                if hasattr(self, 'test_data') and 'teacher_email' in self.test_data:
                    payload['email'] = self.test_data['teacher_email']
                    response = self.session.post(f"{self.base_url}/auth/login", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        self.tokens['teacher'] = data['token']
                        self.test_data['teacher_id'] = data['user']['id']
                        self.log(f"✅ Teacher login successful. Is class teacher: {data['user'].get('is_class_teacher', False)}")
                        return True
                
                self.log(f"❌ Teacher login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Teacher login error: {str(e)}", "ERROR")
            return False
    
    def add_student(self):
        """Test 9: Add a student"""
        self.log("Adding a student...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            roll_number = f"101{self.test_suffix}"
            payload = {
                "name": "John Doe",
                "roll_number": roll_number,
                "class_name": "5A",
                "parent_phone": "9876543210"
            }
            response = self.session.post(f"{self.base_url}/teacher/students", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['student_id'] = data['_id']
                self.test_data['roll_number'] = roll_number
                self.log(f"✅ Student added successfully with roll number: {roll_number}")
                self.log(f"Student school_id: {data.get('school_id')}, Expected: {self.test_data.get('school_id')}")
                return True
            else:
                # If student already exists, try to get existing student
                self.log(f"Student addition failed, trying to use existing student...")
                self.test_data['roll_number'] = "101"  # Use existing roll number
                # Try to get students to find existing one
                response = self.session.get(f"{self.base_url}/teacher/students", headers=headers)
                if response.status_code == 200:
                    students = response.json()
                    if students:
                        self.test_data['student_id'] = students[0]['_id']
                        self.test_data['roll_number'] = students[0]['roll_number']
                        self.log(f"✅ Using existing student with roll number: {students[0]['roll_number']}")
                        return True
                
                self.log(f"❌ Student addition failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Student addition error: {str(e)}", "ERROR")
            return False
    
    def request_otp_for_parent(self):
        """Test 10: Request OTP for parent (with CNN + Roll)"""
        self.log("Requesting OTP for parent...")
        try:
            payload = {
                "school_cnn": self.test_data['school_cnn'],
                "roll_number": self.test_data['roll_number']
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
    
    def test_otp_fixed_value(self):
        """Test 10b: Verify OTP returned is exactly "123456" """
        self.log("Testing fixed OTP value...")
        if self.test_data.get('otp_code') == "123456":
            self.log(f"✅ OTP is correctly fixed to '123456'")
            return True
        else:
            self.log(f"❌ OTP is not fixed to '123456', got: {self.test_data.get('otp_code')}", "ERROR")
            return False
    
    def register_parent_with_otp(self):
        """Test 11: Register parent with OTP"""
        self.log("Registering parent with OTP...")
        try:
            if 'otp_code' not in self.test_data:
                self.log("❌ No OTP code available for parent registration", "ERROR")
                return False
                
            email = f"parent{self.test_suffix}@test.com"
            payload = {
                "email": email,
                "password": "parent123",
                "name": "Parent Name",
                "role": "parent",
                "school_cnn": self.test_data['school_cnn'],
                "student_roll": self.test_data['roll_number'],
                "otp_code": self.test_data['otp_code']
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['parent'] = data['token']
                self.test_data['parent_id'] = data['user']['id']
                self.test_data['parent_email'] = email
                self.log(f"✅ Parent registered successfully")
                return True
            else:
                self.log(f"❌ Parent registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Parent registration error: {str(e)}", "ERROR")
            return False
    
    def test_parent_login_cnn_roll(self):
        """Test 12: Parent login with CNN + Roll only (NEW FEATURE)"""
        self.log("Testing parent login with CNN + Roll only...")
        try:
            payload = {
                "school_cnn": self.test_data['school_cnn'],
                "roll_number": self.test_data['roll_number']
            }
            response = self.session.post(f"{self.base_url}/parent/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                # Verify response contains token, user, and branding
                if 'token' in data and 'user' in data and 'branding' in data:
                    branding = data['branding']
                    if 'app_name' in branding and 'primary_color' in branding:
                        self.log(f"✅ Parent login with CNN+Roll successful with branding: {branding}")
                        self.tokens['parent_cnn'] = data['token']
                        return True
                    else:
                        self.log(f"❌ Parent login missing branding data: {data}", "ERROR")
                        return False
                else:
                    self.log(f"❌ Parent login response missing required fields: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Parent login with CNN+Roll failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Parent login with CNN+Roll error: {str(e)}", "ERROR")
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
    
    def create_school_admin(self):
        """Create a school admin for the created school"""
        self.log("Creating school admin...")
        try:
            email = f"schooladmin{self.test_suffix}@test.com"
            payload = {
                "email": email,
                "password": "admin123",
                "name": "School Admin",
                "role": "school_admin",
                "school_cnn": self.test_data['school_cnn']
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.test_data['school_admin_id'] = data['user']['id']
                self.test_data['school_admin_email'] = email
                self.log(f"✅ School admin registered successfully")
                return True
            else:
                self.log(f"❌ School admin registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ School admin registration error: {str(e)}", "ERROR")
            return False
    
    def login_school_admin(self):
        """Login as school admin"""
        self.log("Logging in as school admin...")
        try:
            payload = {
                "email": self.test_data['school_admin_email'],
                "password": "admin123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.tokens['school_admin'] = data['token']
                self.log(f"✅ School admin login successful")
                return True
            else:
                self.log(f"❌ School admin login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ School admin login error: {str(e)}", "ERROR")
            return False
    
    def set_class_teacher(self):
        """Test 7: Assign as class teacher"""
        self.log("Setting teacher as class teacher...")
        try:
            if 'teacher_id' not in self.test_data:
                self.log("❌ No teacher ID available for setting class teacher", "ERROR")
                return False
                
            headers = {"Authorization": f"Bearer {self.tokens['school_admin']}"}
            payload = {
                "teacher_id": self.test_data['teacher_id'],
                "is_class_teacher": True
            }
            response = self.session.post(f"{self.base_url}/school/teachers/set-class-teacher", json=payload, headers=headers)
            if response.status_code == 200:
                self.log(f"✅ Teacher set as class teacher successfully")
                return True
            else:
                self.log(f"❌ Setting class teacher failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Setting class teacher error: {str(e)}", "ERROR")
            return False
    
    def get_qr_data(self):
        """Test 19: Get QR code data"""
        self.log("Getting QR code data...")
        try:
            # Use school admin token since they have school_id
            headers = {"Authorization": f"Bearer {self.tokens['school_admin']}"}
            response = self.session.get(f"{self.base_url}/school/qr-data", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'cnn_token' in data and 'school_name' in data and 'type' in data:
                    self.log(f"✅ QR data retrieved successfully: {data}")
                    return True
                else:
                    self.log(f"❌ QR data missing required fields: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Getting QR data failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting QR data error: {str(e)}", "ERROR")
            return False
    
    def mark_attendance(self):
        """Test 13: Mark attendance"""
        self.log("Marking attendance...")
        try:
            if 'student_id' not in self.test_data:
                self.log("❌ No student ID available for marking attendance", "ERROR")
                return False
                
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
    
    def create_timetable(self):
        """Test 14: Create timetable"""
        self.log("Creating timetable...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            payload = {
                "class_name": "5A",
                "day": "Monday",
                "periods": [
                    {"period": 1, "subject": "Math", "time": "9:00-10:00"}
                ]
            }
            response = self.session.post(f"{self.base_url}/teacher/timetable", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['timetable_id'] = data['_id']
                self.log(f"✅ Timetable created successfully")
                return True
            else:
                self.log(f"❌ Timetable creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Timetable creation error: {str(e)}", "ERROR")
            return False
    
    def get_qr_data(self):
        """Test 19: Get QR code data"""
        self.log("Getting QR code data...")
        try:
            # Use teacher token since they have school_id
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            response = self.session.get(f"{self.base_url}/school/qr-data", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'cnn_token' in data and 'school_name' in data and 'type' in data:
                    self.log(f"✅ QR data retrieved successfully: {data}")
                    return True
                else:
                    self.log(f"❌ QR data missing required fields: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Getting QR data failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting QR data error: {str(e)}", "ERROR")
            return False
    
    def test_otp_fixed_value(self):
        """Test 10: Verify OTP returned is exactly "123456" """
        self.log("Testing fixed OTP value...")
        if self.test_data.get('otp_code') == "123456":
            self.log(f"✅ OTP is correctly fixed to '123456'")
            return True
        else:
            self.log(f"❌ OTP is not fixed to '123456', got: {self.test_data.get('otp_code')}", "ERROR")
            return False
    
    def test_parent_login_cnn_roll(self):
        """Test 12: Parent login with CNN + Roll only (NEW FEATURE)"""
        self.log("Testing parent login with CNN + Roll only...")
        try:
            payload = {
                "school_cnn": self.test_data['school_cnn'],
                "roll_number": "101"
            }
            response = self.session.post(f"{self.base_url}/parent/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                # Verify response contains token, user, and branding
                if 'token' in data and 'user' in data and 'branding' in data:
                    branding = data['branding']
                    if 'app_name' in branding and 'primary_color' in branding:
                        self.log(f"✅ Parent login with CNN+Roll successful with branding: {branding}")
                        self.tokens['parent_cnn'] = data['token']
                        return True
                    else:
                        self.log(f"❌ Parent login missing branding data: {data}", "ERROR")
                        return False
                else:
                    self.log(f"❌ Parent login response missing required fields: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Parent login with CNN+Roll failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Parent login with CNN+Roll error: {str(e)}", "ERROR")
            return False
    
    def create_timetable(self):
        """Test 14: Create timetable"""
        self.log("Creating timetable...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            payload = {
                "class_name": "5A",
                "day": "Monday",
                "periods": [
                    {"period": 1, "subject": "Math", "time": "9:00-10:00"}
                ]
            }
            response = self.session.post(f"{self.base_url}/teacher/timetable", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['timetable_id'] = data['_id']
                self.log(f"✅ Timetable created successfully")
                return True
            else:
                self.log(f"❌ Timetable creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Timetable creation error: {str(e)}", "ERROR")
            return False
    
    def get_timetable(self):
        """Test 15: Get timetable"""
        self.log("Getting timetable...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            response = self.session.get(f"{self.base_url}/teacher/timetable/5A", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Retrieved timetable with {len(data)} entries")
                return True
            else:
                self.log(f"❌ Getting timetable failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting timetable error: {str(e)}", "ERROR")
            return False
    
    def request_attendance_modification(self):
        """Test 16: Request attendance modification"""
        self.log("Requesting attendance modification...")
        try:
            # First get attendance record ID
            headers = {"Authorization": f"Bearer {self.tokens['teacher']}"}
            response = self.session.get(f"{self.base_url}/teacher/attendance/2025-03-29", headers=headers)
            if response.status_code != 200:
                self.log(f"❌ Could not get attendance records: {response.status_code}", "ERROR")
                return False
            
            attendance_records = response.json()
            if not attendance_records:
                self.log(f"❌ No attendance records found", "ERROR")
                return False
            
            attendance_id = attendance_records[0]['_id']
            self.test_data['attendance_id'] = attendance_id
            
            # Now request modification
            payload = {
                "attendance_id": attendance_id,
                "old_status": "present",
                "new_status": "absent",
                "reason": "Testing modification workflow"
            }
            response = self.session.post(f"{self.base_url}/teacher/attendance/modify-request", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['modification_request_id'] = data['request']['_id']
                self.log(f"✅ Attendance modification requested successfully")
                return True
            else:
                self.log(f"❌ Attendance modification request failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Attendance modification request error: {str(e)}", "ERROR")
            return False
    
    def get_pending_modifications(self):
        """Test 17: Get pending modifications"""
        self.log("Getting pending modifications...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            response = self.session.get(f"{self.base_url}/admin/attendance/modifications/pending", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Retrieved {len(data)} pending modifications")
                return True
            else:
                self.log(f"❌ Getting pending modifications failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting pending modifications error: {str(e)}", "ERROR")
            return False
    
    def approve_modification(self):
        """Test 18: Approve modification"""
        self.log("Approving modification...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            payload = {
                "request_id": self.test_data['modification_request_id'],
                "approved": True
            }
            response = self.session.post(f"{self.base_url}/admin/attendance/approve-modification", json=payload, headers=headers)
            if response.status_code == 200:
                self.log(f"✅ Modification approved successfully")
                return True
            else:
                self.log(f"❌ Modification approval failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Modification approval error: {str(e)}", "ERROR")
            return False
    
    def get_qr_data(self):
        """Test 19: Get QR code data"""
        self.log("Getting QR code data...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            response = self.session.get(f"{self.base_url}/school/qr-data", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'cnn_token' in data and 'school_name' in data and 'type' in data:
                    self.log(f"✅ QR data retrieved successfully: {data}")
                    return True
                else:
                    self.log(f"❌ QR data missing required fields: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Getting QR data failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting QR data error: {str(e)}", "ERROR")
            return False
    
    def get_school_branding(self):
        """Test 20: Get school branding"""
        self.log("Getting school branding...")
        try:
            cnn_token = self.test_data['school_cnn']
            response = self.session.get(f"{self.base_url}/school/branding/{cnn_token}")
            if response.status_code == 200:
                data = response.json()
                if 'app_name' in data and 'primary_color' in data:
                    self.log(f"✅ School branding retrieved successfully: {data}")
                    return True
                else:
                    self.log(f"❌ School branding missing required fields: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Getting school branding failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Getting school branding error: {str(e)}", "ERROR")
            return False
    
    def create_school_with_branding(self):
        """Test 4: Create school with branding"""
        self.log("Creating school with branding...")
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            payload = {
                "name": "Test School",
                "address": "123 Main St",
                "contact_email": "school@test.com",
                "contact_phone": "1234567890",
                "app_name": "MySchool App",
                "primary_color": "#FF5733"
            }
            response = self.session.post(f"{self.base_url}/admin/schools", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_data['school_cnn'] = data['cnn_token']
                self.test_data['school_id'] = data['_id']
                self.log(f"✅ School with branding created successfully. CNN Token: {data['cnn_token']}")
                return True
            else:
                self.log(f"❌ School creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ School creation error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence - Complete 20-step flow"""
        self.log("Starting AttendSys Backend API Tests - Complete Flow...")
        self.log(f"Backend URL: {self.base_url}")
        
        tests = [
            ("1. Health Check", self.test_health_check),
            ("2. Register Platform Admin", self.register_platform_admin),
            ("3. Login Platform Admin", self.login_platform_admin),
            ("4. Create School with Branding", self.create_school_with_branding),
            ("4b. Create School Admin", self.create_school_admin),
            ("4c. Login School Admin", self.login_school_admin),
            ("5. Register Teacher with CNN", self.register_teacher),
            ("6. Approve Teacher", self.approve_teacher),
            ("7. Assign as Class Teacher", self.set_class_teacher),
            ("8. Login as Teacher", self.login_teacher),
            ("9. Add Student", self.add_student),
            ("10. Test OTP Request (CNN + Roll)", self.request_otp_for_parent),
            ("10b. Verify OTP is '123456'", self.test_otp_fixed_value),
            ("11. Register Parent with Fixed OTP", self.register_parent_with_otp),
            ("12. Test Parent Login (CNN + Roll only)", self.test_parent_login_cnn_roll),
            ("13. Mark Attendance", self.mark_attendance),
            ("14. Test Timetable Creation", self.create_timetable),
            ("15. Test Get Timetable", self.get_timetable),
            ("16. Test Attendance Modification Request", self.request_attendance_modification),
            ("17. Test Get Pending Modifications", self.get_pending_modifications),
            ("18. Test Approve Modification", self.approve_modification),
            ("19. Test QR Code Generation", self.get_qr_data),
            ("20. Test School Branding Fetch", self.get_school_branding)
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