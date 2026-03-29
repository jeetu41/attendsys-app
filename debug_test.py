#!/usr/bin/env python3
"""
Debug test to check specific issues
"""

import requests
import json

BACKEND_URL = "https://absence-alert-4.preview.emergentagent.com/api"

def debug_student_school_association():
    """Debug the student-school association issue"""
    
    # Login as platform admin to get schools
    admin_login = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_token = admin_login.json()['token']
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get all schools
        schools_response = requests.get(f"{BACKEND_URL}/admin/schools", headers=headers)
        if schools_response.status_code == 200:
            schools = schools_response.json()
            print(f"✅ Found {len(schools)} schools:")
            for school in schools:
                print(f"  School: {school['name']}, ID: {school['_id']}, CNN: {school['cnn_token']}")
    
    # Login as existing teacher
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": "teacher@test.com",
        "password": "teacher123"
    })
    
    if login_response.status_code != 200:
        print("❌ Teacher login failed")
        return
    
    teacher_data = login_response.json()
    teacher_token = teacher_data['token']
    print(f"✅ Teacher logged in. Is class teacher: {teacher_data['user'].get('is_class_teacher', False)}")
    print(f"Teacher school_id: {teacher_data['user'].get('school_id')}")
    
    # Get students
    headers = {"Authorization": f"Bearer {teacher_token}"}
    students_response = requests.get(f"{BACKEND_URL}/teacher/students", headers=headers)
    
    if students_response.status_code == 200:
        students = students_response.json()
        print(f"✅ Found {len(students)} students")
        for student in students:
            print(f"  Student: {student['name']}, Roll: {student['roll_number']}, School ID: {student.get('school_id')}")
            
            # Find the correct CNN token for this school
            if admin_login.status_code == 200:
                admin_token = admin_login.json()['token']
                headers_admin = {"Authorization": f"Bearer {admin_token}"}
                schools_response = requests.get(f"{BACKEND_URL}/admin/schools", headers=headers_admin)
                if schools_response.status_code == 200:
                    schools = schools_response.json()
                    correct_cnn = None
                    for school in schools:
                        if school['_id'] == student.get('school_id'):
                            correct_cnn = school['cnn_token']
                            break
                    
                    if correct_cnn:
                        print(f"  Using correct CNN: {correct_cnn}")
                        # Try OTP request for this student with correct CNN
                        otp_response = requests.post(f"{BACKEND_URL}/parent/request-otp", json={
                            "school_cnn": correct_cnn,
                            "roll_number": student['roll_number']
                        })
                        
                        print(f"  OTP request for {student['roll_number']}: {otp_response.status_code}")
                        if otp_response.status_code != 200:
                            print(f"    Error: {otp_response.text}")
                        else:
                            print(f"    Success: {otp_response.json()}")
                            break  # Only test one successful case
    else:
        print(f"❌ Failed to get students: {students_response.status_code} - {students_response.text}")

if __name__ == "__main__":
    debug_student_school_association()