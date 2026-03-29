from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
import os
import jwt
import bcrypt
import secrets
import random
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["attendsys"]

# Collections
users_collection = db["users"]
schools_collection = db["schools"]
students_collection = db["students"]
attendance_collection = db["attendance"]
homework_collection = db["homework"]
complaints_collection = db["complaints"]
otps_collection = db["otps"]
notifications_collection = db["notifications"]
timetables_collection = db["timetables"]
attendance_modifications_collection = db["attendance_modifications"]

# JWT Config
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Literal["platform_admin", "school_admin", "teacher", "parent"]
    phone: Optional[str] = None
    school_cnn: Optional[str] = None  # For school_admin, teacher, and parent registration
    student_roll: Optional[str] = None  # For parent registration (combined with school_cnn)
    otp_code: Optional[str] = None  # For parent OTP verification

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SchoolCreate(BaseModel):
    name: str
    address: str
    contact_email: EmailStr
    contact_phone: str
    app_name: Optional[str] = None  # Custom app name for white-label
    logo_base64: Optional[str] = None  # School logo in base64
    primary_color: Optional[str] = "#6366f1"  # Brand color

class StudentCreate(BaseModel):
    name: str
    roll_number: str
    class_name: str
    parent_phone: str
    parent_email: Optional[str] = None

class AttendanceRecord(BaseModel):
    student_id: str
    date: str
    status: Literal["present", "absent", "late", "excused"]
    notes: Optional[str] = None

class AttendanceBatch(BaseModel):
    records: List[AttendanceRecord]

class HomeworkCreate(BaseModel):
    class_name: str
    subject: str
    title: str
    description: str
    due_date: str

class ComplaintCreate(BaseModel):
    recipient_id: str
    message: str

class OTPRequest(BaseModel):
    school_cnn: str
    roll_number: str

class ApproveTeacher(BaseModel):
    teacher_id: str
    approved: bool

class UpdateSubscription(BaseModel):
    user_id: str
    subscription_type: Literal["personal", "school"]
    is_active: bool
    message_balance: int

class SetClassTeacher(BaseModel):
    teacher_id: str
    is_class_teacher: bool

class SetClassTeacher(BaseModel):
    teacher_id: str
    is_class_teacher: bool

class UpdatePhoto(BaseModel):
    photo_base64: str

class UpdateSchoolBranding(BaseModel):
    app_name: Optional[str] = None
    logo_base64: Optional[str] = None
    primary_color: Optional[str] = None

class ParentLogin(BaseModel):
    school_cnn: str
    roll_number: str

class AttendanceModificationRequest(BaseModel):
    attendance_id: str
    old_status: str
    new_status: str
    reason: str

class ApproveModification(BaseModel):
    request_id: str
    approved: bool

class TimetableCreate(BaseModel):
    class_name: str
    day: str
    periods: List[dict]  # [{period: 1, subject: "Math", time: "9:00-10:00"}]

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    user = users_collection.find_one({"_id": ObjectId(payload["user_id"])})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

def generate_cnn_token() -> str:
    return "CNN" + secrets.token_hex(8).upper()

def generate_student_token() -> str:
    return "STU" + secrets.token_hex(6).upper()

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

# Routes
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AttendSys API"}

@app.post("/api/auth/register")
def register(user_data: UserRegister):
    # Check if email exists
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if this is the first user (becomes platform admin)
    user_count = users_collection.count_documents({})
    role = "platform_admin" if user_count == 0 else user_data.role
    
    # Parent registration requires OTP verification
    if user_data.role == "parent":
        if not user_data.school_cnn or not user_data.student_roll or not user_data.otp_code:
            raise HTTPException(status_code=400, detail="Parent registration requires school CNN, student roll number and OTP")
        
        # Verify OTP
        otp_record = otps_collection.find_one({
            "school_cnn": user_data.school_cnn,
            "roll_number": user_data.student_roll,
            "code": user_data.otp_code,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Get student from OTP record
        student_id = otp_record["student_id"]
        
        # Delete used OTP
        otps_collection.delete_one({"_id": otp_record["_id"]})
    
    # School admin and teacher registration with CNN token
    school_id = None
    if user_data.role in ["school_admin", "teacher"] and user_data.school_cnn:
        school = schools_collection.find_one({"cnn_token": user_data.school_cnn})
        if not school:
            raise HTTPException(status_code=400, detail="Invalid school CNN token")
        school_id = str(school["_id"])
    
    user_doc = {
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "name": user_data.name,
        "role": role,
        "phone": user_data.phone,
        "photo_base64": None,  # Profile photo
        "school_id": school_id,
        "is_approved": True if role in ["platform_admin", "parent"] else False,
        "is_class_teacher": False,
        "subscription_type": None,
        "subscription_active": False,
        "message_balance": 0,
        "created_at": datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Link parent to student
    if user_data.role == "parent" and student_id:
        students_collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"parent_id": user_id, "parent_email": user_data.email}}
        )
    
    token = create_access_token({"user_id": user_id, "role": role})
    
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "role": role,
            "is_approved": user_doc["is_approved"]
        }
    }

@app.post("/api/auth/login")
def login(credentials: UserLogin):
    user = users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": str(user["_id"]), "role": user["role"]})
    
    return {
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "is_approved": user.get("is_approved", False),
            "is_class_teacher": user.get("is_class_teacher", False),
            "school_id": user.get("school_id"),
            "subscription_active": user.get("subscription_active", False),
            "message_balance": user.get("message_balance", 0)
        }
    }

@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Platform Admin Routes
@app.post("/api/admin/schools")
def create_school(school_data: SchoolCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Only platform admins can create schools")
    
    cnn_token = generate_cnn_token()
    
    school_doc = {
        "name": school_data.name,
        "address": school_data.address,
        "contact_email": school_data.contact_email,
        "contact_phone": school_data.contact_phone,
        "cnn_token": cnn_token,
        "app_name": school_data.app_name or school_data.name,
        "logo_base64": school_data.logo_base64,
        "primary_color": school_data.primary_color or "#6366f1",
        "subscription_type": "school",
        "subscription_active": False,
        "message_balance": 0,
        "created_at": datetime.utcnow()
    }
    
    result = schools_collection.insert_one(school_doc)
    school_doc["_id"] = str(result.inserted_id)
    
    return school_doc

@app.get("/api/admin/schools")
def list_schools(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    schools = list(schools_collection.find())
    for school in schools:
        school["_id"] = str(school["_id"])
    
    return schools

@app.get("/api/admin/teachers/pending")
def get_pending_teachers(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    teachers = list(users_collection.find({"role": "teacher", "is_approved": False}))
    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
        if teacher.get("school_id"):
            school = schools_collection.find_one({"_id": ObjectId(teacher["school_id"])})
            teacher["school_name"] = school["name"] if school else "Unknown"
    
    return teachers

@app.post("/api/admin/teachers/approve")
def approve_teacher(data: ApproveTeacher, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    users_collection.update_one(
        {"_id": ObjectId(data.teacher_id)},
        {"$set": {"is_approved": data.approved}}
    )
    
    return {"message": "Teacher approval status updated"}

@app.post("/api/admin/subscriptions/update")
def update_subscription(data: UpdateSubscription, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    users_collection.update_one(
        {"_id": ObjectId(data.user_id)},
        {"$set": {
            "subscription_type": data.subscription_type,
            "subscription_active": data.is_active,
            "message_balance": data.message_balance
        }}
    )
    
    return {"message": "Subscription updated"}

@app.get("/api/admin/stats")
def get_admin_stats(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "platform_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    total_schools = schools_collection.count_documents({})
    total_teachers = users_collection.count_documents({"role": "teacher"})
    pending_teachers = users_collection.count_documents({"role": "teacher", "is_approved": False})
    total_students = students_collection.count_documents({})
    total_parents = users_collection.count_documents({"role": "parent"})
    
    return {
        "total_schools": total_schools,
        "total_teachers": total_teachers,
        "pending_teachers": pending_teachers,
        "total_students": total_students,
        "total_parents": total_parents
    }

# School Admin Routes
@app.get("/api/school/teachers")
def get_school_teachers(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "school_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    teachers = list(users_collection.find({
        "role": "teacher",
        "school_id": current_user.get("school_id")
    }))
    
    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
    
    return teachers

@app.post("/api/school/teachers/set-class-teacher")
def set_class_teacher(data: SetClassTeacher, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "school_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    users_collection.update_one(
        {"_id": ObjectId(data.teacher_id), "school_id": current_user.get("school_id")},
        {"$set": {"is_class_teacher": data.is_class_teacher}}
    )
    
    return {"message": "Class teacher status updated"}

@app.get("/api/school/stats")
def get_school_stats(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "school_admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    school_id = current_user.get("school_id")
    
    total_teachers = users_collection.count_documents({"role": "teacher", "school_id": school_id})
    class_teachers = users_collection.count_documents({"role": "teacher", "school_id": school_id, "is_class_teacher": True})
    total_students = students_collection.count_documents({"school_id": school_id})
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_attendance = attendance_collection.count_documents({"date": today, "school_id": school_id})
    
    return {
        "total_teachers": total_teachers,
        "class_teachers": class_teachers,
        "total_students": total_students,
        "today_attendance": today_attendance
    }

# Teacher Routes
@app.post("/api/teacher/students")
def add_student(student_data: StudentCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can add students")
    
    # Check if roll number exists
    if students_collection.find_one({"roll_number": student_data.roll_number}):
        raise HTTPException(status_code=400, detail="Roll number already exists")
    
    student_token = generate_student_token()
    
    student_doc = {
        "name": student_data.name,
        "roll_number": student_data.roll_number,
        "class_name": student_data.class_name,
        "parent_phone": student_data.parent_phone,
        "parent_email": student_data.parent_email,
        "parent_id": None,
        "teacher_id": current_user["_id"],
        "school_id": current_user.get("school_id"),
        "student_token": student_token,
        "created_at": datetime.utcnow()
    }
    
    result = students_collection.insert_one(student_doc)
    student_doc["_id"] = str(result.inserted_id)
    
    return student_doc

@app.get("/api/teacher/students")
def get_my_students(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    students = list(students_collection.find({"teacher_id": current_user["_id"]}))
    
    for student in students:
        student["_id"] = str(student["_id"])
        
        # Calculate attendance percentage
        total_records = attendance_collection.count_documents({"student_id": str(student["_id"])})
        present_records = attendance_collection.count_documents({
            "student_id": str(student["_id"]),
            "status": {"$in": ["present", "late"]}
        })
        
        student["attendance_percentage"] = round((present_records / total_records * 100) if total_records > 0 else 0, 1)
        student["total_days"] = total_records
    
    return students

@app.post("/api/teacher/attendance")
def mark_attendance(attendance_data: AttendanceBatch, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    records_to_insert = []
    
    for record in attendance_data.records:
        # Check if attendance already marked for this student on this date
        existing = attendance_collection.find_one({
            "student_id": record.student_id,
            "date": record.date
        })
        
        if existing:
            # Update existing record
            attendance_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "status": record.status,
                    "notes": record.notes,
                    "updated_at": datetime.utcnow()
                }}
            )
        else:
            # Insert new record
            records_to_insert.append({
                "student_id": record.student_id,
                "teacher_id": current_user["_id"],
                "school_id": current_user.get("school_id"),
                "date": record.date,
                "status": record.status,
                "notes": record.notes,
                "synced": True,
                "created_at": datetime.utcnow()
            })
        
        # Send notification to parent if absent
        if record.status == "absent":
            student = students_collection.find_one({"_id": ObjectId(record.student_id)})
            if student and student.get("parent_id"):
                notifications_collection.insert_one({
                    "user_id": student["parent_id"],
                    "title": "Absence Alert",
                    "message": f"{student['name']} was marked absent on {record.date}",
                    "type": "absence",
                    "read": False,
                    "created_at": datetime.utcnow()
                })
    
    if records_to_insert:
        attendance_collection.insert_many(records_to_insert)
    
    return {"message": f"Attendance marked for {len(attendance_data.records)} students"}

@app.get("/api/teacher/attendance/{date}")
def get_attendance_by_date(date: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    records = list(attendance_collection.find({
        "teacher_id": current_user["_id"],
        "date": date
    }))
    
    for record in records:
        record["_id"] = str(record["_id"])
    
    return records

@app.post("/api/teacher/homework")
def post_homework(homework_data: HomeworkCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    homework_doc = {
        "teacher_id": current_user["_id"],
        "school_id": current_user.get("school_id"),
        "class_name": homework_data.class_name,
        "subject": homework_data.subject,
        "title": homework_data.title,
        "description": homework_data.description,
        "due_date": homework_data.due_date,
        "created_at": datetime.utcnow()
    }
    
    result = homework_collection.insert_one(homework_doc)
    homework_doc["_id"] = str(result.inserted_id)
    
    # Notify all parents of students in this class
    students = students_collection.find({
        "teacher_id": current_user["_id"],
        "class_name": homework_data.class_name
    })
    
    for student in students:
        if student.get("parent_id"):
            notifications_collection.insert_one({
                "user_id": student["parent_id"],
                "title": f"New Homework: {homework_data.subject}",
                "message": f"{homework_data.title} - Due: {homework_data.due_date}",
                "type": "homework",
                "read": False,
                "created_at": datetime.utcnow()
            })
    
    return homework_doc

@app.get("/api/teacher/homework")
def get_my_homework(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    homework = list(homework_collection.find({"teacher_id": current_user["_id"]}).sort("created_at", -1))
    
    for hw in homework:
        hw["_id"] = str(hw["_id"])
    
    return homework

# Parent Routes
@app.post("/api/parent/request-otp")
def request_otp(otp_request: OTPRequest):
    # Find school by CNN token
    school = schools_collection.find_one({"cnn_token": otp_request.school_cnn})
    if not school:
        raise HTTPException(status_code=404, detail="Invalid school CNN token")
    
    # Find student by roll number in this specific school
    student = students_collection.find_one({
        "roll_number": otp_request.roll_number,
        "school_id": str(school["_id"])
    })
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in this school")
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Delete any existing OTPs for this school + roll number combination
    otps_collection.delete_many({
        "school_cnn": otp_request.school_cnn,
        "roll_number": otp_request.roll_number
    })
    
    # Store OTP (expires in 10 minutes)
    otps_collection.insert_one({
        "school_cnn": otp_request.school_cnn,
        "roll_number": otp_request.roll_number,
        "code": otp_code,
        "phone": student["parent_phone"],
        "student_id": str(student["_id"]),
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "created_at": datetime.utcnow()
    })
    
    # In production, send SMS here
    # For now, return OTP in response (development only)
    return {
        "message": "OTP sent to registered phone number",
        "otp": otp_code,  # Remove this in production
        "phone": student["parent_phone"][-4:]  # Show last 4 digits
    }

@app.get("/api/parent/children")
def get_my_children(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    students = list(students_collection.find({"parent_id": current_user["_id"]}))
    
    for student in students:
        student["_id"] = str(student["_id"])
        
        # Calculate attendance percentage
        total_records = attendance_collection.count_documents({"student_id": str(student["_id"])})
        present_records = attendance_collection.count_documents({
            "student_id": str(student["_id"]),
            "status": {"$in": ["present", "late"]}
        })
        
        student["attendance_percentage"] = round((present_records / total_records * 100) if total_records > 0 else 0, 1)
        student["total_days"] = total_records
        student["present_days"] = present_records
    
    return students

@app.get("/api/parent/attendance/{student_id}")
def get_student_attendance(student_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Verify this is the parent's child
    student = students_collection.find_one({"_id": ObjectId(student_id), "parent_id": current_user["_id"]})
    if not student:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    records = list(attendance_collection.find({"student_id": student_id}).sort("date", -1).limit(30))
    
    for record in records:
        record["_id"] = str(record["_id"])
    
    return records

@app.get("/api/parent/homework/{student_id}")
def get_student_homework(student_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Verify this is the parent's child
    student = students_collection.find_one({"_id": ObjectId(student_id), "parent_id": current_user["_id"]})
    if not student:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    homework = list(homework_collection.find({
        "class_name": student["class_name"],
        "teacher_id": student["teacher_id"]
    }).sort("created_at", -1).limit(20))
    
    for hw in homework:
        hw["_id"] = str(hw["_id"])
    
    return homework

# Notifications
@app.get("/api/notifications")
def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = list(notifications_collection.find({"user_id": current_user["_id"]}).sort("created_at", -1).limit(50))
    
    for notif in notifications:
        notif["_id"] = str(notif["_id"])
    
    return notifications

@app.post("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    notifications_collection.update_one(
        {"_id": ObjectId(notification_id), "user_id": current_user["_id"]},
        {"$set": {"read": True}}
    )
    
    return {"message": "Notification marked as read"}

# Complaints
@app.post("/api/complaints")
def create_complaint(complaint_data: ComplaintCreate, current_user: dict = Depends(get_current_user)):
    complaint_doc = {
        "sender_id": current_user["_id"],
        "sender_name": current_user["name"],
        "sender_role": current_user["role"],
        "recipient_id": complaint_data.recipient_id,
        "message": complaint_data.message,
        "status": "open",
        "created_at": datetime.utcnow()
    }
    
    result = complaints_collection.insert_one(complaint_doc)
    complaint_doc["_id"] = str(result.inserted_id)
    
    # Notify recipient
    notifications_collection.insert_one({
        "user_id": complaint_data.recipient_id,
        "title": "New Complaint",
        "message": f"You have received a complaint from {current_user['name']}",
        "type": "complaint",
        "read": False,
        "created_at": datetime.utcnow()
    })
    
    return complaint_doc

@app.get("/api/complaints")
def get_my_complaints(current_user: dict = Depends(get_current_user)):
    complaints = list(complaints_collection.find({
        "$or": [
            {"sender_id": current_user["_id"]},
            {"recipient_id": current_user["_id"]}
        ]
    }).sort("created_at", -1))
    
    for complaint in complaints:
        complaint["_id"] = str(complaint["_id"])
    
    return complaints


# Photo Management
@app.post("/api/user/photo")
def update_photo(photo_data: UpdatePhoto, current_user: dict = Depends(get_current_user)):
    users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"photo_base64": photo_data.photo_base64}}
    )
    return {"message": "Photo updated successfully"}

# School Branding Management
@app.post("/api/school/branding")
def update_school_branding(branding_data: UpdateSchoolBranding, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["platform_admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update school branding")
    
    # Get school ID
    school_id = current_user.get("school_id")
    if not school_id and current_user["role"] == "platform_admin":
        raise HTTPException(status_code=400, detail="Platform admin must specify school_id")
    
    update_data = {}
    if branding_data.app_name:
        update_data["app_name"] = branding_data.app_name
    if branding_data.logo_base64:
        update_data["logo_base64"] = branding_data.logo_base64
    if branding_data.primary_color:
        update_data["primary_color"] = branding_data.primary_color
    
    if update_data:
        schools_collection.update_one(
            {"_id": ObjectId(school_id)},
            {"$set": update_data}
        )
    
    return {"message": "School branding updated successfully"}

@app.get("/api/school/branding/{cnn_token}")
def get_school_branding(cnn_token: str):
    school = schools_collection.find_one({"cnn_token": cnn_token})
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    return {
        "app_name": school.get("app_name", "AttendSys"),
        "logo_base64": school.get("logo_base64"),
        "primary_color": school.get("primary_color", "#6366f1"),
        "school_name": school["name"]
    }

# Parent Login without Email/Password (CNN + Roll Number)
@app.post("/api/parent/login")
def parent_login(login_data: ParentLogin):
    # Find school by CNN
    school = schools_collection.find_one({"cnn_token": login_data.school_cnn})
    if not school:
        raise HTTPException(status_code=404, detail="Invalid school CNN token")
    
    # Find student by roll number in this school
    student = students_collection.find_one({
        "roll_number": login_data.roll_number,
        "school_id": str(school["_id"])
    })
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in this school")
    
    # Check if parent is already linked
    if not student.get("parent_id"):
        raise HTTPException(status_code=400, detail="No parent linked to this student. Please complete registration first.")
    
    # Get parent user
    parent = users_collection.find_one({"_id": ObjectId(student["parent_id"])})
    if not parent:
        raise HTTPException(status_code=404, detail="Parent account not found")
    
    # Create token
    token = create_access_token({"user_id": str(parent["_id"]), "role": "parent"})
    
    return {
        "token": token,
        "user": {
            "id": str(parent["_id"]),
            "name": parent["name"],
            "role": "parent",
            "phone": parent.get("phone")
        },
        "branding": {
            "app_name": school.get("app_name", "AttendSys"),
            "logo_base64": school.get("logo_base64"),
            "primary_color": school.get("primary_color", "#6366f1"),
            "school_name": school["name"]
        }
    }

# Timetable Management (Class Teacher)
@app.post("/api/teacher/timetable")
def create_timetable(timetable_data: TimetableCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher" or not current_user.get("is_class_teacher"):
        raise HTTPException(status_code=403, detail="Only class teachers can manage timetables")
    
    # Delete existing timetable for this class and day
    timetables_collection.delete_many({
        "class_name": timetable_data.class_name,
        "day": timetable_data.day,
        "teacher_id": current_user["_id"]
    })
    
    timetable_doc = {
        "teacher_id": current_user["_id"],
        "class_name": timetable_data.class_name,
        "day": timetable_data.day,
        "periods": timetable_data.periods,
        "school_id": current_user.get("school_id"),
        "created_at": datetime.utcnow()
    }
    
    result = timetables_collection.insert_one(timetable_doc)
    timetable_doc["_id"] = str(result.inserted_id)
    
    return timetable_doc

@app.get("/api/teacher/timetable/{class_name}")
def get_timetable(class_name: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["teacher", "parent"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    timetables = list(timetables_collection.find({"class_name": class_name}))
    for tt in timetables:
        tt["_id"] = str(tt["_id"])
    
    return timetables

# Attendance Modification Request (Teacher)
@app.post("/api/teacher/attendance/modify-request")
def request_attendance_modification(
    request_data: AttendanceModificationRequest,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can request modifications")
    
    # Get attendance record
    attendance = attendance_collection.find_one({"_id": ObjectId(request_data.attendance_id)})
    if not attendance or attendance["teacher_id"] != current_user["_id"]:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Create modification request
    modification_doc = {
        "attendance_id": request_data.attendance_id,
        "teacher_id": current_user["_id"],
        "school_id": current_user.get("school_id"),
        "student_id": attendance["student_id"],
        "date": attendance["date"],
        "old_status": request_data.old_status,
        "new_status": request_data.new_status,
        "reason": request_data.reason,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = attendance_modifications_collection.insert_one(modification_doc)
    modification_doc["_id"] = str(result.inserted_id)
    
    return {"message": "Modification request submitted", "request": modification_doc}

# Admin: Approve/Reject Attendance Modifications
@app.post("/api/admin/attendance/approve-modification")
def approve_attendance_modification(
    approval_data: ApproveModification,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["platform_admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can approve modifications")
    
    # Get modification request
    modification = attendance_modifications_collection.find_one({"_id": ObjectId(approval_data.request_id)})
    if not modification:
        raise HTTPException(status_code=404, detail="Modification request not found")
    
    if approval_data.approved:
        # Update attendance record
        attendance_collection.update_one(
            {"_id": ObjectId(modification["attendance_id"])},
            {"$set": {
                "status": modification["new_status"],
                "modified_at": datetime.utcnow(),
                "modified_by": current_user["_id"]
            }}
        )
        
        # Update modification request status
        attendance_modifications_collection.update_one(
            {"_id": ObjectId(approval_data.request_id)},
            {"$set": {
                "status": "approved",
                "approved_by": current_user["_id"],
                "approved_at": datetime.utcnow()
            }}
        )
        
        return {"message": "Modification approved and attendance updated"}
    else:
        # Reject modification
        attendance_modifications_collection.update_one(
            {"_id": ObjectId(approval_data.request_id)},
            {"$set": {
                "status": "rejected",
                "rejected_by": current_user["_id"],
                "rejected_at": datetime.utcnow()
            }}
        )
        
        return {"message": "Modification request rejected"}

@app.get("/api/admin/attendance/modifications/pending")
def get_pending_modifications(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["platform_admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can view modification requests")
    
    query = {"status": "pending"}
    if current_user["role"] == "school_admin":
        query["school_id"] = current_user.get("school_id")
    
    modifications = list(attendance_modifications_collection.find(query).sort("created_at", -1))
    
    for mod in modifications:
        mod["_id"] = str(mod["_id"])
        # Get student name
        student = students_collection.find_one({"_id": ObjectId(mod["student_id"])})
        if student:
            mod["student_name"] = student["name"]
            mod["class_name"] = student["class_name"]
    
    return modifications

# Generate QR Code Data for School CNN
@app.get("/api/school/qr-data")
def get_school_qr_data(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["platform_admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Only admins can generate QR codes")
    
    school_id = current_user.get("school_id")
    if not school_id:
        raise HTTPException(status_code=400, detail="No school associated with this account")
    
    school = schools_collection.find_one({"_id": ObjectId(school_id)})
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # QR data contains CNN token
    qr_data = {
        "cnn_token": school["cnn_token"],
        "school_name": school["name"],
        "type": "school_registration"
    }
    
    return qr_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
