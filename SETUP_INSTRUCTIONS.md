# AttendSys - Setup & GitHub Push Instructions

## 📦 What's Included

This ZIP contains your complete AttendSys school attendance management system:

### Backend (FastAPI)
- `backend/server.py` - All API endpoints (30+ routes)
- `backend/requirements.txt` - Python dependencies
- `backend/.env` - Environment variables (MongoDB URL)

### Frontend (Expo/React Native)
- `frontend/app/` - All screens and routes
  - `(admin)/` - Platform admin portal
  - `(school)/` - School admin portal
  - `(teacher)/` - Teacher portal (complete)
  - `(parent)/` - Parent portal (complete)
  - `login.tsx` - Login screen
  - `register.tsx` - Registration screen
- `frontend/src/store/` - Zustand stores (auth, branding)
- `frontend/package.json` - Dependencies
- `frontend/app.json` - Expo configuration

### Other Files
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation
- `config.json` - App configuration

---

## 🚀 Push to GitHub

### Step 1: Extract the ZIP
```bash
unzip attendsys-app.zip
cd attendsys-app
```

### Step 2: Initialize Git (if not already)
```bash
git init
git add .
git commit -m "Complete AttendSys school attendance management system"
```

### Step 3: Add Your GitHub Remote
```bash
git remote add origin https://github.com/jeetu41/attendsys-app.git
```

### Step 4: Push to GitHub
```bash
git branch -M main
git push -u origin main
```

When prompted:
- **Username:** jeetu41
- **Password:** Use your GitHub Personal Access Token (NOT your password!)

### Create GitHub Personal Access Token:
1. Go to: https://github.com/settings/tokens/new
2. Note: "AttendSys Push"
3. Expiration: 30 days
4. Scopes: Check "repo"
5. Click "Generate token"
6. Copy the token (starts with ghp_)
7. Use this token as your password when pushing

---

## 💻 Local Development Setup

### Backend Setup

1. **Navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup MongoDB:**
- Install MongoDB locally OR use MongoDB Atlas
- Update `backend/.env` with your MongoDB URL:
```
MONGO_URL=mongodb://localhost:27017
# OR
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/attendsys
```

5. **Run backend:**
```bash
python server.py
# Runs on http://localhost:8001
```

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
yarn install
# OR
npm install
```

3. **Update API URL:**
- Edit `frontend/src/store/authStore.ts`
- Change line 6:
```javascript
const API_URL = 'http://localhost:8001';
```

4. **Start Expo:**
```bash
npx expo start
```

5. **Run on device:**
- **Mobile:** Scan QR code with Expo Go app
- **Web:** Press 'w' to open in browser
- **iOS Simulator:** Press 'i'
- **Android Emulator:** Press 'a'

---

## 🔑 Test Credentials

### Platform Admin (First User)
- Will be auto-created as platform admin
- Email: admin@test.com
- Password: admin123

### OTP for Testing
- Fixed OTP: **123456**

### Parent Login
- Use CNN Token + Student Roll Number
- No password needed!

---

## 📱 Features Included

✅ **4 User Portals:**
- Platform Admin (manage schools, approve teachers)
- School Admin (manage teachers in school)
- Teacher (attendance, students, homework, timetable)
- Parent (view attendance, homework, notifications)

✅ **Core Features:**
- Attendance marking (offline-capable)
- Student management
- Timetable creation
- Homework posting
- White-label branding (custom logo, colors, app name)
- OTP verification
- Parent CNN+Roll login
- Attendance modification with admin approval
- In-app notifications
- Message quota tracking

✅ **Technical Features:**
- JWT authentication
- MongoDB database
- Base64 image storage
- Offline sync with AsyncStorage
- Role-based access control

---

## 📂 Project Structure

```
attendsys-app/
├── backend/
│   ├── server.py          # FastAPI app with all endpoints
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
│
├── frontend/
│   ├── app/              # Expo Router screens
│   │   ├── (admin)/      # Admin portal
│   │   ├── (school)/     # School admin portal
│   │   ├── (teacher)/    # Teacher portal
│   │   ├── (parent)/     # Parent portal
│   │   ├── login.tsx     # Login screen
│   │   └── register.tsx  # Registration
│   │
│   ├── src/
│   │   └── store/        # Zustand state management
│   │
│   ├── package.json      # Dependencies
│   └── app.json          # Expo config
│
├── .gitignore
└── README.md
```

---

## 🔧 Environment Variables

### Backend `.env`
```
MONGO_URL=mongodb://localhost:27017
JWT_SECRET=your-secret-key-change-in-production
```

### Frontend `.env`
```
EXPO_PUBLIC_BACKEND_URL=http://localhost:8001
```

**Note:** When deploying, update these URLs to your production servers!

---

## 🌐 Deployment

### Backend (FastAPI)
- Deploy to: Heroku, Railway, Render, DigitalOcean
- Set environment variables in hosting platform
- Install dependencies from requirements.txt
- Run: `uvicorn server:app --host 0.0.0.0 --port 8001`

### Frontend (Expo)
- **Web:** `npx expo export:web` then deploy static files
- **Mobile:** Build with EAS:
  ```bash
  npx eas build --platform android
  npx eas build --platform ios
  ```

---

## 📖 API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

---

## 🐛 Troubleshooting

**Backend won't start:**
- Check MongoDB is running
- Verify Python version (3.8+)
- Check .env file exists

**Frontend can't connect to backend:**
- Update API_URL in authStore.ts
- Check backend is running on port 8001
- Verify CORS settings in server.py

**App shows "Unmatched Route":**
- Clear Metro cache: `npx expo start -c`
- Restart Expo dev server

---

## 📞 Support

For issues or questions:
1. Check existing GitHub issues
2. Create new issue with error details
3. Include steps to reproduce

---

## 📄 License

MIT License - Feel free to use and modify!

---

**Built with ❤️ using Expo, FastAPI, and MongoDB**
