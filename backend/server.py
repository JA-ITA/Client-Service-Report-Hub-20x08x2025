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

# Enhanced Stage 3 Models - Dynamic Reporting System
class DynamicField(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    section: str  # Category/section for grouping fields (e.g., "Personal Info", "Project Details")
    label: str  # Display name for the field
    field_type: str  # text, number, date, dropdown, multiselect, textarea, file, checkbox
    choices: Optional[List[str]] = None  # For dropdown/multiselect fields
    validation: Optional[dict] = None  # Validation rules (min, max, pattern, etc.)
    placeholder: Optional[str] = None
    help_text: Optional[str] = None  # Additional guidance for users
    deleted: bool = False  # Soft delete functionality
    created_by: str  # Admin user ID who created this field
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DynamicFieldCreate(BaseModel):
    section: str
    label: str
    field_type: str
    choices: Optional[List[str]] = None
    validation: Optional[dict] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None

class DynamicFieldUpdate(BaseModel):
    section: Optional[str] = None
    label: Optional[str] = None
    field_type: Optional[str] = None
    choices: Optional[List[str]] = None
    validation: Optional[dict] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    deleted: Optional[bool] = None

class ReportField(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    label: str
    field_type: str  # text, number, date, dropdown, checkbox, textarea, multiselect, file
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

class ReportTemplateEnhanced(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str = "General"  # Category for organizing templates
    fields: List[ReportField] = []
    dynamic_field_ids: List[str] = []  # References to DynamicField IDs
    active: bool = True
    created_by: str  # Admin user ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReportTemplateCreateEnhanced(BaseModel):
    name: str
    description: str
    category: str = "General"
    fields: List[ReportFieldCreate] = []
    dynamic_field_ids: List[str] = []  # IDs of DynamicFields to include

class ReportSubmissionEnhanced(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    user_id: str
    location_id: Optional[str] = None
    report_period: str  # Format: "2025-01" for January 2025
    data: dict  # Dynamic field data
    status: str = "draft"  # draft, submitted, reviewed, approved, rejected
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None  # Admin user ID who reviewed
    review_notes: Optional[str] = None
    attachments: List[str] = []  # File paths for uploaded files
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Keep original models for backward compatibility
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
    
    # Enhanced Stage 3 indexes
    await db.dynamic_fields.create_index([("section", 1)])
    await db.dynamic_fields.create_index([("deleted", 1)])
    await db.dynamic_fields.create_index([("created_by", 1)])
    
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
    
    # Create default dynamic fields
    admin_user = await db.users.find_one({"username": "admin"})
    admin_id = admin_user["id"] if admin_user else str(uuid.uuid4())
    
    default_fields = [
        {
            "id": str(uuid.uuid4()),
            "section": "Basic Information",
            "label": "Employee Name",
            "field_type": "text",
            "placeholder": "Enter employee full name",
            "help_text": "Enter the employee's full name as it appears in official records",
            "deleted": False,
            "created_by": admin_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "section": "Basic Information",
            "label": "Department",
            "field_type": "dropdown",
            "choices": ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"],
            "help_text": "Select the department the employee belongs to",
            "deleted": False,
            "created_by": admin_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "section": "Performance Metrics",
            "label": "Productivity Score",
            "field_type": "number",
            "placeholder": "0-100",
            "validation": {"min": 0, "max": 100},
            "help_text": "Rate productivity on a scale of 0-100",
            "deleted": False,
            "created_by": admin_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "section": "Performance Metrics",
            "label": "Key Accomplishments",
            "field_type": "textarea",
            "placeholder": "List key accomplishments for the month...",
            "help_text": "Provide detailed description of major accomplishments",
            "deleted": False,
            "created_by": admin_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "section": "Project Details",
            "label": "Project Status",
            "field_type": "dropdown",
            "choices": ["Not Started", "In Progress", "On Hold", "Completed", "Cancelled"],
            "help_text": "Select the current status of the main project",
            "deleted": False,
            "created_by": admin_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "section": "Time Management",
            "label": "Hours Worked",
            "field_type": "number",
            "placeholder": "Enter total hours",
            "validation": {"min": 0, "max": 744},  # Max hours in a month
            "help_text": "Total hours worked during the reporting period",
            "deleted": False,
            "created_by": admin_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    for field_data in default_fields:
        existing_field = await db.dynamic_fields.find_one({"label": field_data["label"], "section": field_data["section"]})
        if not existing_field:
            await db.dynamic_fields.insert_one(field_data)
            logger.info(f"Created dynamic field: {field_data['label']} in {field_data['section']}")
    
    # Create default report template (keep existing logic)
    default_template = await db.report_templates.find_one({"name": "Monthly Progress Report"})
    if not default_template:
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
            "created_by": admin_id,
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

# Enhanced Stage 3: Dynamic Field Management APIs (Admin Only)
@api_router.get("/admin/dynamic-fields", response_model=List[DynamicField])
async def get_all_dynamic_fields(current_user: User = Depends(get_admin_user), include_deleted: bool = False):
    """Get all dynamic fields with optional inclusion of deleted fields"""
    filter_query = {} if include_deleted else {"deleted": {"$ne": True}}
    fields = await db.dynamic_fields.find(filter_query).to_list(1000)
    return [DynamicField(**field) for field in fields]

@api_router.get("/admin/dynamic-fields/sections")
async def get_field_sections(current_user: User = Depends(get_admin_user)):
    """Get all unique field sections for organizing fields"""
    sections = await db.dynamic_fields.distinct("section", {"deleted": {"$ne": True}})
    return {"sections": sections}

@api_router.post("/admin/dynamic-fields", response_model=DynamicField)
async def create_dynamic_field(field_data: DynamicFieldCreate, current_user: User = Depends(get_admin_user)):
    """Create a new dynamic field"""
    # Validate field type
    valid_types = ["text", "number", "date", "dropdown", "multiselect", "textarea", "file", "checkbox"]
    if field_data.field_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field type. Must be one of: {', '.join(valid_types)}"
        )
    
    # For dropdown/multiselect, ensure choices are provided
    if field_data.field_type in ["dropdown", "multiselect"] and not field_data.choices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choices must be provided for dropdown and multiselect fields"
        )
    
    new_field = DynamicField(
        **field_data.dict(),
        created_by=current_user.id
    )
    await db.dynamic_fields.insert_one(new_field.dict())
    return new_field

@api_router.put("/admin/dynamic-fields/{field_id}", response_model=DynamicField)
async def update_dynamic_field(field_id: str, field_data: DynamicFieldUpdate, current_user: User = Depends(get_admin_user)):
    """Update a dynamic field"""
    # Check if field exists
    existing_field = await db.dynamic_fields.find_one({"id": field_id})
    if not existing_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dynamic field not found"
        )
    
    # Validate field type if being updated
    if field_data.field_type:
        valid_types = ["text", "number", "date", "dropdown", "multiselect", "textarea", "file", "checkbox"]
        if field_data.field_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid field type. Must be one of: {', '.join(valid_types)}"
            )
    
    # Prepare update data
    update_data = {k: v for k, v in field_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.dynamic_fields.update_one(
        {"id": field_id},
        {"$set": update_data}
    )
    
    updated_field = await db.dynamic_fields.find_one({"id": field_id})
    return DynamicField(**updated_field)

@api_router.delete("/admin/dynamic-fields/{field_id}")
async def soft_delete_dynamic_field(field_id: str, current_user: User = Depends(get_admin_user)):
    """Soft delete a dynamic field"""
    result = await db.dynamic_fields.update_one(
        {"id": field_id},
        {"$set": {"deleted": True, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dynamic field not found"
        )
    return {"message": "Dynamic field deleted successfully"}

@api_router.post("/admin/dynamic-fields/{field_id}/restore")
async def restore_dynamic_field(field_id: str, current_user: User = Depends(get_admin_user)):
    """Restore a soft-deleted dynamic field"""
    result = await db.dynamic_fields.update_one(
        {"id": field_id},
        {"$set": {"deleted": False, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dynamic field not found"
        )
    return {"message": "Dynamic field restored successfully"}

# Admin routes - System Statistics (backward compatibility)
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

# Enhanced Report Template Management with Dynamic Fields
@api_router.post("/admin/report-templates/from-fields", response_model=ReportTemplate)
async def create_template_from_dynamic_fields(
    template_name: str,
    template_description: str,
    field_ids: List[str],
    template_category: str = "General",
    current_user: User = Depends(get_admin_user)
):
    """Create a report template from selected dynamic fields"""
    # Check if template name already exists
    existing_template = await db.report_templates.find_one({"name": template_name})
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report template name already exists"
        )
    
    # Fetch the selected dynamic fields
    selected_fields = await db.dynamic_fields.find({
        "id": {"$in": field_ids},
        "deleted": {"$ne": True}
    }).to_list(1000)
    
    if len(selected_fields) != len(field_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some selected fields were not found or are deleted"
        )
    
    # Convert dynamic fields to report fields
    report_fields = []
    for i, field in enumerate(selected_fields):
        report_field = {
            "id": str(uuid.uuid4()),
            "name": field["label"].lower().replace(" ", "_"),
            "label": field["label"],
            "field_type": field["field_type"],
            "required": False,  # Default to not required, can be customized
            "options": field.get("choices"),
            "placeholder": field.get("placeholder"),
            "validation": field.get("validation"),
            "order": i + 1
        }
        report_fields.append(report_field)
    
    # Create the new template
    new_template = ReportTemplate(
        name=template_name,
        description=template_description,
        fields=report_fields,
        created_by=current_user.id
    )
    
    await db.report_templates.insert_one(new_template.dict())
    return new_template

# System Analytics and Enhanced Statistics
@api_router.get("/admin/analytics")
async def get_system_analytics(current_user: User = Depends(get_admin_user)):
    """Get enhanced system analytics and metrics"""
    # Basic user and location stats
    total_users = await db.users.count_documents({})
    approved_users = await db.users.count_documents({"approved": True})
    pending_users = await db.users.count_documents({"approved": False})
    total_locations = await db.locations.count_documents({})
    admin_users = await db.users.count_documents({"role": "ADMIN"})
    regular_users = await db.users.count_documents({"role": "USER"})
    
    # Report and field statistics
    total_templates = await db.report_templates.count_documents({"active": True})
    total_fields = await db.dynamic_fields.count_documents({"deleted": {"$ne": True}})
    total_reports = await db.report_submissions.count_documents({})
    submitted_reports = await db.report_submissions.count_documents({"status": "submitted"})
    draft_reports = await db.report_submissions.count_documents({"status": "draft"})
    
    # Time-based analytics
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    recent_registrations = await db.users.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    recent_submissions = await db.report_submissions.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    monthly_submissions = await db.report_submissions.count_documents({
        "created_at": {"$gte": thirty_days_ago}
    })
    
    # Field usage analytics
    field_sections = await db.dynamic_fields.distinct("section", {"deleted": {"$ne": True}})
    section_stats = {}
    for section in field_sections:
        count = await db.dynamic_fields.count_documents({
            "section": section,
            "deleted": {"$ne": True}
        })
        section_stats[section] = count
    
    return {
        # User metrics
        "total_users": total_users,
        "approved_users": approved_users,
        "pending_users": pending_users,
        "admin_users": admin_users,
        "regular_users": regular_users,
        "recent_registrations": recent_registrations,
        
        # System metrics
        "total_locations": total_locations,
        "total_templates": total_templates,
        "total_fields": total_fields,
        
        # Report metrics
        "total_reports": total_reports,
        "submitted_reports": submitted_reports,
        "draft_reports": draft_reports,
        "recent_submissions": recent_submissions,
        "monthly_submissions": monthly_submissions,
        
        # Field analytics
        "field_sections": field_sections,
        "section_stats": section_stats,
        
        # Calculated metrics
        "approval_rate": round((approved_users / total_users * 100) if total_users > 0 else 0, 1),
        "submission_rate": round((submitted_reports / total_reports * 100) if total_reports > 0 else 0, 1)
    }

# Report Templates for Users (Enhanced)
@api_router.get("/report-templates/enhanced", response_model=List[ReportTemplate])
async def get_enhanced_report_templates(current_user: User = Depends(get_current_user)):
    """Get active report templates with enhanced metadata"""
    templates = await db.report_templates.find({"active": True}).to_list(1000)
    return [ReportTemplate(**template) for template in templates]

# Report Template Management APIs (Admin Only)
@api_router.get("/admin/report-templates", response_model=List[ReportTemplate])
async def get_all_report_templates(current_user: User = Depends(get_admin_user)):
    templates = await db.report_templates.find().to_list(1000)
    return [ReportTemplate(**template) for template in templates]

@api_router.post("/admin/report-templates", response_model=ReportTemplate)
async def create_report_template(template_data: ReportTemplateCreate, current_user: User = Depends(get_admin_user)):
    # Check if template name already exists
    existing_template = await db.report_templates.find_one({"name": template_data.name})
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report template name already exists"
        )
    
    # Convert fields to include IDs
    fields_with_ids = []
    for field in template_data.fields:
        field_dict = field.dict()
        field_dict["id"] = str(uuid.uuid4())
        fields_with_ids.append(field_dict)
    
    new_template = ReportTemplate(
        **template_data.dict(exclude={"fields"}),
        fields=fields_with_ids,
        created_by=current_user.id
    )
    await db.report_templates.insert_one(new_template.dict())
    return new_template

@api_router.put("/admin/report-templates/{template_id}", response_model=ReportTemplate)
async def update_report_template(template_id: str, template_data: ReportTemplateUpdate, current_user: User = Depends(get_admin_user)):
    # Check if template exists
    existing_template = await db.report_templates.find_one({"id": template_id})
    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    
    update_data = {}
    if template_data.name is not None:
        # Check if new name already exists (excluding current template)
        name_exists = await db.report_templates.find_one({
            "id": {"$ne": template_id},
            "name": template_data.name
        })
        if name_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report template name already exists"
            )
        update_data["name"] = template_data.name
    
    if template_data.description is not None:
        update_data["description"] = template_data.description
    
    if template_data.active is not None:
        update_data["active"] = template_data.active
    
    if template_data.fields is not None:
        # Convert fields to include IDs
        fields_with_ids = []
        for field in template_data.fields:
            field_dict = field.dict()
            field_dict["id"] = str(uuid.uuid4())
            fields_with_ids.append(field_dict)
        update_data["fields"] = fields_with_ids
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.report_templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    updated_template = await db.report_templates.find_one({"id": template_id})
    return ReportTemplate(**updated_template)

@api_router.delete("/admin/report-templates/{template_id}")
async def delete_report_template(template_id: str, current_user: User = Depends(get_admin_user)):
    # Check if template has any submissions
    submissions_exist = await db.report_submissions.find_one({"template_id": template_id})
    if submissions_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete template. It has existing submissions."
        )
    
    result = await db.report_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    return {"message": "Report template deleted successfully"}

# Report Templates for Users
@api_router.get("/report-templates", response_model=List[ReportTemplate])
async def get_active_report_templates(current_user: User = Depends(get_current_user)):
    templates = await db.report_templates.find({"active": True}).to_list(1000)
    return [ReportTemplate(**template) for template in templates]

@api_router.get("/report-templates/{template_id}", response_model=ReportTemplate)
async def get_report_template(template_id: str, current_user: User = Depends(get_current_user)):
    template = await db.report_templates.find_one({"id": template_id, "active": True})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    return ReportTemplate(**template)

# Report Submission APIs
@api_router.get("/reports", response_model=List[ReportSubmissionResponse])
async def get_user_reports(current_user: User = Depends(get_current_user)):
    # Get user's own reports
    reports = await db.report_submissions.find({"user_id": current_user.id}).to_list(1000)
    
    # Enrich with template and location names
    enriched_reports = []
    for report in reports:
        # Get template name
        template = await db.report_templates.find_one({"id": report["template_id"]})
        template_name = template["name"] if template else "Unknown Template"
        
        # Get location name
        location_name = None
        if report.get("location_id"):
            location = await db.locations.find_one({"id": report["location_id"]})
            location_name = location["name"] if location else None
        
        enriched_report = ReportSubmissionResponse(
            **report,
            template_name=template_name,
            username=current_user.username,
            location_name=location_name
        )
        enriched_reports.append(enriched_report)
    
    return enriched_reports

@api_router.get("/admin/reports", response_model=List[ReportSubmissionResponse])
async def get_all_reports(current_user: User = Depends(get_admin_user)):
    # Get all reports for admin
    reports = await db.report_submissions.find().to_list(1000)
    
    # Enrich with template, user, and location names
    enriched_reports = []
    for report in reports:
        # Get template name
        template = await db.report_templates.find_one({"id": report["template_id"]})
        template_name = template["name"] if template else "Unknown Template"
        
        # Get user name
        user = await db.users.find_one({"id": report["user_id"]})
        username = user["username"] if user else "Unknown User"
        
        # Get location name
        location_name = None
        if report.get("location_id"):
            location = await db.locations.find_one({"id": report["location_id"]})
            location_name = location["name"] if location else None
        
        enriched_report = ReportSubmissionResponse(
            **report,
            template_name=template_name,
            username=username,
            location_name=location_name
        )
        enriched_reports.append(enriched_report)
    
    return enriched_reports

@api_router.post("/reports", response_model=ReportSubmission)
async def create_or_update_report(report_data: ReportSubmissionCreate, current_user: User = Depends(get_current_user)):
    # Check if template exists and is active
    template = await db.report_templates.find_one({"id": report_data.template_id, "active": True})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found or inactive"
        )
    
    # Check if report already exists for this user, template, and period
    existing_report = await db.report_submissions.find_one({
        "user_id": current_user.id,
        "template_id": report_data.template_id,
        "report_period": report_data.report_period
    })
    
    if existing_report:
        # Update existing report
        update_data = {
            "data": report_data.data,
            "status": report_data.status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if report_data.status == "submitted" and existing_report.get("status") != "submitted":
            update_data["submitted_at"] = datetime.now(timezone.utc)
        
        await db.report_submissions.update_one(
            {"id": existing_report["id"]},
            {"$set": update_data}
        )
        
        updated_report = await db.report_submissions.find_one({"id": existing_report["id"]})
        return ReportSubmission(**updated_report)
    else:
        # Create new report
        new_report = ReportSubmission(
            **report_data.dict(),
            user_id=current_user.id,
            location_id=current_user.location_id,
            submitted_at=datetime.now(timezone.utc) if report_data.status == "submitted" else None
        )
        await db.report_submissions.insert_one(new_report.dict())
        return new_report

@api_router.get("/reports/{report_id}", response_model=ReportSubmissionResponse)
async def get_report(report_id: str, current_user: User = Depends(get_current_user)):
    report = await db.report_submissions.find_one({"id": report_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions - users can only see their own reports, admins can see all
    if current_user.role != "ADMIN" and report["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )
    
    # Enrich with names
    template = await db.report_templates.find_one({"id": report["template_id"]})
    template_name = template["name"] if template else "Unknown Template"
    
    user = await db.users.find_one({"id": report["user_id"]})
    username = user["username"] if user else "Unknown User"
    
    location_name = None
    if report.get("location_id"):
        location = await db.locations.find_one({"id": report["location_id"]})
        location_name = location["name"] if location else None
    
    return ReportSubmissionResponse(
        **report,
        template_name=template_name,
        username=username,
        location_name=location_name
    )

# Advanced Report Management - Search, Filter, Export
@api_router.get("/admin/reports/search")
async def search_reports(
    current_user: User = Depends(get_admin_user),
    search_term: Optional[str] = None,
    status: Optional[str] = None,
    template_id: Optional[str] = None,
    user_id: Optional[str] = None,
    location_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Advanced search and filtering for reports"""
    # Build query
    query = {}
    
    if search_term:
        # Search in report data fields
        query["$text"] = {"$search": search_term}
    
    if status:
        query["status"] = status
    
    if template_id:
        query["template_id"] = template_id
    
    if user_id:
        query["user_id"] = user_id
    
    if location_id:
        query["location_id"] = location_id
    
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query["created_at"] = date_query
    
    # Calculate pagination
    skip = (page - 1) * limit
    
    # Get total count
    total_count = await db.report_submissions.count_documents(query)
    
    # Get reports
    reports_cursor = db.report_submissions.find(query).skip(skip).limit(limit).sort("created_at", -1)
    reports = await reports_cursor.to_list(limit)
    
    # Enrich with names
    enriched_reports = []
    for report in reports:
        template = await db.report_templates.find_one({"id": report["template_id"]})
        template_name = template["name"] if template else "Unknown Template"
        
        user = await db.users.find_one({"id": report["user_id"]})
        username = user["username"] if user else "Unknown User"
        
        location_name = None
        if report.get("location_id"):
            location = await db.locations.find_one({"id": report["location_id"]})
            location_name = location["name"] if location else None
        
        enriched_report = ReportSubmissionResponse(
            **report,
            template_name=template_name,
            username=username,
            location_name=location_name
        )
        enriched_reports.append(enriched_report)
    
    return {
        "reports": enriched_reports,
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }

@api_router.post("/admin/reports/bulk-actions")
async def bulk_report_actions(
    action: str,
    report_ids: List[str],
    current_user: User = Depends(get_admin_user)
):
    """Perform bulk actions on reports"""
    valid_actions = ["delete", "approve", "reject", "mark_reviewed"]
    
    if action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        )
    
    if not report_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No report IDs provided"
        )
    
    # Check that all reports exist
    existing_reports = await db.report_submissions.find({"id": {"$in": report_ids}}).to_list(1000)
    if len(existing_reports) != len(report_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some report IDs were not found"
        )
    
    if action == "delete":
        result = await db.report_submissions.delete_many({"id": {"$in": report_ids}})
        return {"message": f"Successfully deleted {result.deleted_count} reports"}
    
    elif action in ["approve", "reject", "mark_reviewed"]:
        update_data = {
            "reviewed_at": datetime.now(timezone.utc),
            "reviewed_by": current_user.id
        }
        
        if action == "approve":
            update_data["status"] = "approved"
        elif action == "reject":
            update_data["status"] = "rejected"
        elif action == "mark_reviewed":
            update_data["status"] = "reviewed"
        
        result = await db.report_submissions.update_many(
            {"id": {"$in": report_ids}},
            {"$set": update_data}
        )
        
        return {"message": f"Successfully {action}ed {result.modified_count} reports"}

@api_router.get("/admin/reports/export")
async def export_reports(
    current_user: User = Depends(get_admin_user),
    format: str = "csv",
    status: Optional[str] = None,
    template_id: Optional[str] = None,
    user_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Export reports in CSV or JSON format"""
    # Build query
    query = {}
    
    if status:
        query["status"] = status
    if template_id:
        query["template_id"] = template_id
    if user_id:
        query["user_id"] = user_id
    
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query["created_at"] = date_query
    
    # Get reports
    reports = await db.report_submissions.find(query).to_list(1000)
    
    # Enrich with names
    export_data = []
    for report in reports:
        template = await db.report_templates.find_one({"id": report["template_id"]})
        template_name = template["name"] if template else "Unknown Template"
        
        user = await db.users.find_one({"id": report["user_id"]})
        username = user["username"] if user else "Unknown User"
        
        location_name = None
        if report.get("location_id"):
            location = await db.locations.find_one({"id": report["location_id"]})
            location_name = location["name"] if location else None
        
        # Flatten report data for export
        flat_data = {
            "report_id": report["id"],
            "template_name": template_name,
            "username": username,
            "location_name": location_name or "",
            "report_period": report["report_period"],
            "status": report["status"],
            "submitted_at": report.get("submitted_at", "").isoformat() if report.get("submitted_at") else "",
            "created_at": report["created_at"].isoformat(),
            "updated_at": report["updated_at"].isoformat()
        }
        
        # Add report data fields
        for key, value in report.get("data", {}).items():
            flat_data[f"data_{key}"] = str(value) if value is not None else ""
        
        export_data.append(flat_data)
    
    if format.lower() == "csv":
        # For now, return the data structure - in production you'd generate actual CSV
        return {
            "format": "csv",
            "data": export_data,
            "filename": f"reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    else:
        return {
            "format": "json",
            "data": export_data,
            "filename": f"reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }

# Enhanced Template Builder with Preview
@api_router.post("/admin/report-templates/preview")
async def preview_template(
    template_data: dict,
    current_user: User = Depends(get_admin_user)
):
    """Generate a preview of how a template will look"""
    try:
        # Validate the template structure
        if "name" not in template_data or "fields" not in template_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template must have name and fields"
            )
        
        # Generate preview HTML
        html_preview = f"""
        <div class="template-preview">
            <h3>{template_data.get('name', 'Untitled Template')}</h3>
            <p>{template_data.get('description', '')}</p>
            <form class="preview-form">
        """
        
        for field in template_data.get('fields', []):
            field_html = generate_field_html_preview(field)
            html_preview += field_html
        
        html_preview += """
            </form>
        </div>
        """
        
        return {
            "preview_html": html_preview,
            "field_count": len(template_data.get('fields', [])),
            "estimated_completion_time": len(template_data.get('fields', [])) * 2  # 2 minutes per field estimate
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating preview: {str(e)}"
        )

def generate_field_html_preview(field: dict) -> str:
    """Generate HTML preview for a single field"""
    field_type = field.get('field_type', 'text')
    label = field.get('label', 'Untitled Field')
    placeholder = field.get('placeholder', '')
    required = field.get('required', False)
    
    html = f'<div class="field-preview mb-3">'
    html += f'<label class="form-label">{label}'
    if required:
        html += ' <span class="text-danger">*</span>'
    html += '</label>'
    
    if field_type == 'text':
        html += f'<input type="text" class="form-control" placeholder="{placeholder}" disabled>'
    elif field_type == 'textarea':
        html += f'<textarea class="form-control" placeholder="{placeholder}" rows="3" disabled></textarea>'
    elif field_type == 'number':
        html += f'<input type="number" class="form-control" placeholder="{placeholder}" disabled>'
    elif field_type == 'date':
        html += f'<input type="date" class="form-control" disabled>'
    elif field_type == 'dropdown':
        html += '<select class="form-control" disabled>'
        html += '<option>Select an option...</option>'
        for option in field.get('options', []):
            html += f'<option>{option}</option>'
        html += '</select>'
    elif field_type == 'checkbox':
        html += f'<div class="form-check">'
        html += f'<input type="checkbox" class="form-check-input" disabled>'
        html += f'<label class="form-check-label">{label}</label>'
        html += '</div>'
    elif field_type == 'file':
        html += '<input type="file" class="form-control" disabled>'
    
    html += '</div>'
    return html

# Enhanced Field Type Support
@api_router.get("/admin/field-types")
async def get_supported_field_types(current_user: User = Depends(get_admin_user)):
    """Get all supported field types with their configurations"""
    field_types = {
        "text": {
            "label": "Text Input",
            "description": "Single line text input",
            "supports_validation": True,
            "supports_placeholder": True,
            "supports_choices": False
        },
        "textarea": {
            "label": "Text Area",
            "description": "Multi-line text input",
            "supports_validation": True,
            "supports_placeholder": True,
            "supports_choices": False
        },
        "number": {
            "label": "Number Input",
            "description": "Numeric input with validation",
            "supports_validation": True,
            "supports_placeholder": True,
            "supports_choices": False
        },
        "date": {
            "label": "Date Picker",
            "description": "Date selection input",
            "supports_validation": True,
            "supports_placeholder": False,
            "supports_choices": False
        },
        "dropdown": {
            "label": "Dropdown Select",
            "description": "Single selection from predefined options",
            "supports_validation": False,
            "supports_placeholder": False,
            "supports_choices": True
        },
        "multiselect": {
            "label": "Multi-Select",
            "description": "Multiple selection from predefined options",
            "supports_validation": False,
            "supports_placeholder": False,
            "supports_choices": True
        },
        "checkbox": {
            "label": "Checkbox",
            "description": "Boolean yes/no input",
            "supports_validation": False,
            "supports_placeholder": False,
            "supports_choices": False
        },
        "file": {
            "label": "File Upload",
            "description": "File attachment input",
            "supports_validation": True,
            "supports_placeholder": False,
            "supports_choices": False
        }
    }
    
    return {"field_types": field_types}

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