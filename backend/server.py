from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from pymongo import IndexModel

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Create the main app
app = FastAPI(title="MonthlyReportsHub", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Location(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LocationCreate(BaseModel):
    name: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    password_hash: Optional[str] = None
    role: str = "USER"  # USER or ADMIN
    location_id: Optional[str] = None
    approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    location_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    location_id: Optional[str] = None
    approved: bool
    created_at: datetime

# New Stage 3 Models - Dynamic Reporting
class ReportField(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    label: str
    field_type: str  # text, number, date, dropdown, checkbox, textarea
    required: bool = False
    options: Optional[List[str]] = None  # For dropdown fields
    placeholder: Optional[str] = None
    validation: Optional[dict] = None  # Custom validation rules
    order: int = 0

class ReportFieldCreate(BaseModel):
    name: str
    label: str
    field_type: str
    required: bool = False
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None
    validation: Optional[dict] = None
    order: int = 0

class ReportTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    fields: List[ReportField] = []
    active: bool = True
    created_by: str  # Admin user ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReportTemplateCreate(BaseModel):
    name: str
    description: str
    fields: List[ReportFieldCreate] = []

class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[ReportFieldCreate]] = None
    active: Optional[bool] = None

class ReportSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    user_id: str
    location_id: Optional[str] = None
    report_period: str  # Format: "2025-01" for January 2025
    data: dict  # Dynamic field data
    status: str = "draft"  # draft, submitted, reviewed, approved
    submitted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReportSubmissionCreate(BaseModel):
    template_id: str
    report_period: str
    data: dict
    status: str = "draft"

class ReportSubmissionUpdate(BaseModel):
    data: Optional[dict] = None
    status: Optional[str] = None

class ReportSubmissionResponse(BaseModel):
    id: str
    template_id: str
    template_name: str
    user_id: str
    username: str
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    report_period: str
    data: dict
    status: str
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Database initialization
async def init_database():
    # Create indexes
    await db.users.create_index([("username", 1)], unique=True)
    await db.users.create_index([("email", 1)], unique=True)
    await db.locations.create_index([("name", 1)], unique=True)
    
    # New indexes for reporting
    await db.report_templates.create_index([("name", 1)], unique=True)
    await db.report_submissions.create_index([("user_id", 1)])
    await db.report_submissions.create_index([("template_id", 1)])
    await db.report_submissions.create_index([("report_period", 1)])
    await db.report_submissions.create_index([("user_id", 1), ("template_id", 1), ("report_period", 1)], unique=True)
    
    # Seed admin user
    admin_exists = await db.users.find_one({"username": "admin"})
    if not admin_exists:
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@monthlyreporthub.com",
            "password_hash": get_password_hash("admin123"),
            "role": "ADMIN",
            "location_id": None,
            "approved": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(admin_user)
        logger.info("Admin user created: username=admin, password=admin123")
    
    # Create default location
    default_location = await db.locations.find_one({"name": "Main Office"})
    if not default_location:
        default_loc = {
            "id": str(uuid.uuid4()),
            "name": "Main Office",
            "created_at": datetime.now(timezone.utc)
        }
        await db.locations.insert_one(default_loc)
        logger.info("Default location created: Main Office")
    
    # Create default report template
    default_template = await db.report_templates.find_one({"name": "Monthly Progress Report"})
    if not default_template:
        admin_user = await db.users.find_one({"username": "admin"})
        default_template = {
            "id": str(uuid.uuid4()),
            "name": "Monthly Progress Report",
            "description": "Standard monthly progress and metrics report",
            "fields": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "key_achievements",
                    "label": "Key Achievements",
                    "field_type": "textarea",
                    "required": True,
                    "placeholder": "List your key achievements for this month...",
                    "order": 1
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "challenges",
                    "label": "Challenges Faced",
                    "field_type": "textarea",
                    "required": True,
                    "placeholder": "Describe any challenges you encountered...",
                    "order": 2
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "goals_next_month",
                    "label": "Goals for Next Month",
                    "field_type": "textarea",
                    "required": True,
                    "placeholder": "What are your goals for next month?",
                    "order": 3
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "satisfaction_rating",
                    "label": "Overall Satisfaction",
                    "field_type": "dropdown",
                    "required": True,
                    "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
                    "order": 4
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "hours_worked",
                    "label": "Total Hours Worked",
                    "field_type": "number",
                    "required": True,
                    "placeholder": "Enter total hours worked this month",
                    "order": 5
                }
            ],
            "active": True,
            "created_by": admin_user["id"] if admin_user else str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.report_templates.insert_one(default_template)
        logger.info("Default report template created: Monthly Progress Report")

# Authentication routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({
        "$or": [{"username": user_data.username}, {"email": user_data.email}]
    })
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Validate location if provided
    if user_data.location_id:
        location = await db.locations.find_one({"id": user_data.location_id})
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location"
            )
    
    # Create user
    user_dict = user_data.dict()
    user_dict["password_hash"] = get_password_hash(user_data.password)
    del user_dict["password"]
    
    new_user = User(**user_dict)
    await db.users.insert_one(new_user.dict())
    
    return UserResponse(**new_user.dict())

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"username": login_data.username})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["approved"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not approved yet. Please contact administrator."
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    user_obj = User(**user)
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Location routes
@api_router.get("/locations", response_model=List[Location])
async def get_locations():
    locations = await db.locations.find().to_list(1000)
    return [Location(**location) for location in locations]

@api_router.post("/locations", response_model=Location)
async def create_location(location_data: LocationCreate, current_user: User = Depends(get_admin_user)):
    # Check if location exists
    existing_location = await db.locations.find_one({"name": location_data.name})
    if existing_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location already exists"
        )
    
    new_location = Location(**location_data.dict())
    await db.locations.insert_one(new_location.dict())
    return new_location

# Admin routes - User Management
@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_admin_user)):
    users = await db.users.find().to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.put("/admin/users/{user_id}/approve")
async def approve_user(user_id: str, current_user: User = Depends(get_admin_user)):
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"approved": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User approved successfully"}

@api_router.put("/admin/users/{user_id}/role")
async def update_user_role(user_id: str, role_data: dict, current_user: User = Depends(get_admin_user)):
    if role_data.get("role") not in ["USER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be USER or ADMIN"
        )
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role_data["role"]}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"User role updated to {role_data['role']} successfully"}

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(get_admin_user)):
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

# Admin routes - Location Management
@api_router.get("/admin/locations", response_model=List[Location])
async def get_all_locations_admin(current_user: User = Depends(get_admin_user)):
    locations = await db.locations.find().to_list(1000)
    return [Location(**location) for location in locations]

@api_router.put("/admin/locations/{location_id}")
async def update_location(location_id: str, location_data: LocationCreate, current_user: User = Depends(get_admin_user)):
    # Check if new name already exists (excluding current location)
    existing_location = await db.locations.find_one({
        "id": {"$ne": location_id},
        "name": location_data.name
    })
    if existing_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location name already exists"
        )
    
    result = await db.locations.update_one(
        {"id": location_id},
        {"$set": {"name": location_data.name}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return {"message": "Location updated successfully"}

@api_router.delete("/admin/locations/{location_id}")
async def delete_location(location_id: str, current_user: User = Depends(get_admin_user)):
    # Check if location is in use by any users
    users_with_location = await db.users.find_one({"location_id": location_id})
    if users_with_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete location. It is assigned to users."
        )
    
    result = await db.locations.delete_one({"id": location_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return {"message": "Location deleted successfully"}

# Admin routes - System Statistics  
@api_router.get("/admin/stats")
async def get_system_stats(current_user: User = Depends(get_admin_user)):
    total_users = await db.users.count_documents({})
    approved_users = await db.users.count_documents({"approved": True})
    pending_users = await db.users.count_documents({"approved": False})
    total_locations = await db.locations.count_documents({})
    admin_users = await db.users.count_documents({"role": "ADMIN"})
    regular_users = await db.users.count_documents({"role": "USER"})
    
    # Recent registrations (last 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_registrations = await db.users.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    return {
        "total_users": total_users,
        "approved_users": approved_users,
        "pending_users": pending_users,
        "total_locations": total_locations,
        "admin_users": admin_users,
        "regular_users": regular_users,
        "recent_registrations": recent_registrations
    }

# Basic routes
@api_router.get("/")
async def root():
    return {"message": "MonthlyReportsHub API", "version": "1.0.0"}

@api_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}! This is a protected route."}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_database()
    logger.info("MonthlyReportsHub started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()