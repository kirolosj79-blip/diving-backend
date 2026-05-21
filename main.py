from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid, datetime

app = FastAPI(title="Diving Conference API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

users_db: List[dict] = [
    {"id":"admin-001","name":"Admin","email":"admin@diving.com","password":"admin123","role":"admin","created_at":str(datetime.datetime.now())}
]

activities_db: List[dict] = [
    {"id":"a1","name":"Opening Ceremony","name_ar":"حفل الافتتاح","type":"lecture","icon":"🎤","time":"9:00 AM","time_ar":"٩:٠٠ ص","points":10,"desc":"Welcome to the Diving Conference!","desc_ar":"أهلاً بك في مؤتمر دايفينج!","visible":True},
    {"id":"a2","name":"Deep Dive Workshop","name_ar":"ورشة الغوص العميق","type":"workshop","icon":"🤿","time":"10:30 AM","time_ar":"١٠:٣٠ ص","points":25,"desc":"Hands-on workshop on advanced techniques.","desc_ar":"ورشة عملية في التقنيات المتقدمة.","visible":True},
    {"id":"a3","name":"Marine Life Quiz","name_ar":"مسابقة الحياة البحرية","type":"game","icon":"🐠","time":"12:00 PM","time_ar":"١٢:٠٠ م","points":20,"desc":"Test your knowledge!","desc_ar":"اختبر معلوماتك!","visible":True},
    {"id":"a4","name":"Faith & Ocean Talk","name_ar":"محاضرة: الإيمان والمحيط","type":"lecture","icon":"🌊","time":"2:00 PM","time_ar":"٢:٠٠ م","points":15,"desc":"Spiritual reflection on creation.","desc_ar":"تأمل روحي في الخلق.","visible":True},
    {"id":"a5","name":"Buddy System Workshop","name_ar":"ورشة نظام الزميل","type":"workshop","icon":"🧑‍🤝‍🧑","time":"3:30 PM","time_ar":"٣:٣٠ م","points":20,"desc":"Teamwork and brotherhood in diving.","desc_ar":"العمل الجماعي في الغوص.","visible":True},
    {"id":"a6","name":"Bonus: Early Bird","name_ar":"بونص: الحضور المبكر","type":"bonus","icon":"⭐","time":"8:30 AM","time_ar":"٨:٣٠ ص","points":30,"desc":"Bonus for arriving early.","desc_ar":"نقاط للحضور المبكر.","visible":True},
]

attendance_db: List[dict] = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RegisterReq(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "user"

class LoginReq(BaseModel):
    email: str
    password: str

class AttendanceReq(BaseModel):
    user_id: str
    activity_id: str
    user_name: Optional[str] = ""

class ActivityReq(BaseModel):
    name: str
    name_ar: Optional[str] = ""
    type: str
    icon: Optional[str] = "📌"
    time: Optional[str] = "TBA"
    points: int
    desc: Optional[str] = ""
    desc_ar: Optional[str] = ""

class ToggleReq(BaseModel):
    visible: bool

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/")
def root():
    return {"message": "🤿 Diving Conference API", "users": len(users_db), "activities": len(activities_db), "attendance": len(attendance_db)}

@app.post("/auth/register", status_code=201)
def register(req: RegisterReq):
    if any(u["email"] == req.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered!")
    user = {"id": str(uuid.uuid4()), "name": req.name, "email": req.email, "password": req.password, "role": "user", "created_at": str(datetime.datetime.now())}
    users_db.append(user)
    return {"message": "Account created!", "user": {k:v for k,v in user.items() if k!="password"}}

@app.post("/auth/login")
def login(req: LoginReq):
    user = next((u for u in users_db if u["email"]==req.email and u["password"]==req.password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong email or password!")
    return {"message": "Welcome back!", "token": f"token_{user['id']}", "user": {k:v for k,v in user.items() if k!="password"}}

@app.get("/auth/users")
def get_users():
    return [{"id":u["id"],"name":u["name"],"email":u["email"],"role":u["role"]} for u in users_db]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ACTIVITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/activities")
def get_activities(all: bool = False):
    if all: return activities_db
    return [a for a in activities_db if a["visible"]]

@app.post("/activities", status_code=201)
def add_activity(req: ActivityReq):
    act = {"id": "c"+str(uuid.uuid4())[:8], **req.dict(), "visible": True}
    activities_db.append(act)
    return {"message": "Activity added!", "activity": act}

@app.put("/activities/{act_id}/toggle")
def toggle_activity(act_id: str, req: ToggleReq):
    act = next((a for a in activities_db if a["id"]==act_id), None)
    if not act: raise HTTPException(status_code=404, detail="Activity not found")
    act["visible"] = req.visible
    return {"message": f"Activity {'visible' if req.visible else 'hidden'}", "activity": act}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ATTENDANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/attendance", status_code=201)
def check_in(req: AttendanceReq):
    # Check duplicate
    if any(a["user_id"]==req.user_id and a["activity_id"]==req.activity_id for a in attendance_db):
        raise HTTPException(status_code=400, detail="Already checked in!")
    activity = next((a for a in activities_db if a["id"]==req.activity_id), None)
    if not activity: raise HTTPException(status_code=404, detail="Activity not found")
    record = {"id": str(uuid.uuid4()), "user_id": req.user_id, "user_name": req.user_name, "activity_id": req.activity_id, "activity_name": activity["name"], "points": activity["points"], "timestamp": str(datetime.datetime.now())}
    attendance_db.append(record)
    return {"message": f"Checked in! +{activity['points']} points", "record": record}

@app.get("/attendance")
def get_attendance(user_id: Optional[str] = None):
    if user_id: return [a for a in attendance_db if a["user_id"]==user_id]
    return attendance_db

@app.get("/attendance/stats")
def get_stats():
    user_points = {}
    for rec in attendance_db:
        uid = rec["user_id"]
        user_points[uid] = user_points.get(uid, 0) + rec["points"]
    top = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
    return {"total_checkins": len(attendance_db), "user_points": dict(top), "top_user": top[0] if top else None}
