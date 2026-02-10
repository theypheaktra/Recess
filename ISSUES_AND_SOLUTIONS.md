# RECESS IMS - Issues & Solutions

**Date:** 2026-02-10  
**Status:** CRITICAL - System Non-Functional

---

## 🚨 CRITICAL ISSUES (BLOCKING)

### Issue #1: No Backend API Server
**Status:** ❌ NOT STARTED  
**Priority:** P0 - CRITICAL  
**Blocking:** Entire system functionality

#### Problem
- Frontend exists but operates on static JSON files
- No API server to process requests
- All business logic missing
- Cannot save any data

#### Impact
- System cannot be used in production
- All data is dummy/static
- No user authentication
- No transaction processing

#### Solution Required
```python
# Backend Structure Needed
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── order.py
│   │   └── settlement.py
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── orders.py
│   │   ├── settlements.py
│   │   └── projects.py
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Helper functions
├── alembic/                 # Database migrations
├── tests/
├── requirements.txt
└── .env
```

#### Implementation Steps
1. **Set up FastAPI project** (Day 1)
   ```bash
   pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt]
   ```

2. **Create database models** (Day 2-3)
   - Implement 14 core tables
   - Set up relationships
   - Add constraints and indexes

3. **Build authentication** (Day 4-5)
   - JWT token generation
   - Password hashing
   - Login/logout endpoints

4. **Implement core APIs** (Week 2-3)
   - Purchase orders API
   - Settlements API
   - Projects/Episodes/Cuts API

5. **Testing** (Week 4)
   - Unit tests
   - Integration tests
   - Load testing

#### Estimated Effort
- **Developer:** 1 senior FastAPI developer
- **Timeline:** 4 weeks (MVP)
- **Cost:** $15,000-25,000 USD

---

### Issue #2: Database Not Implemented
**Status:** ❌ NOT STARTED  
**Priority:** P0 - CRITICAL  
**Blocking:** Data persistence

#### Problem
- No PostgreSQL database set up
- No schema implementation
- Data exists only as 14 dummy JSON files
- All changes lost on page refresh

#### Impact
- Cannot save any user data
- Cannot track orders or settlements
- Cannot maintain audit trail
- No data integrity

#### Solution Required
```sql
-- Core Tables Needed

-- 1. Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_jp VARCHAR(100),
    role_level INTEGER CHECK (role_level BETWEEN 0 AND 7),
    tier INTEGER CHECK (tier BETWEEN 0 AND 2),
    org_id INTEGER REFERENCES organizations(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Organizations Table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_jp VARCHAR(200),
    type VARCHAR(20) CHECK (type IN ('committee', 'prime', 'sub')),
    tier INTEGER CHECK (tier BETWEEN 0 AND 2),
    business_no VARCHAR(50),
    bank_account VARCHAR(100),
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Projects Table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_no VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_jp VARCHAR(200),
    client_org_id INTEGER REFERENCES organizations(id),
    type VARCHAR(20) CHECK (type IN ('TVA', 'Movie', 'OVA', 'Web')),
    total_episodes INTEGER,
    total_cuts INTEGER,
    completed_cuts INTEGER DEFAULT 0,
    progress DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    budget DECIMAL(15,2),
    deadline DATE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Purchase Orders Table (CRITICAL)
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(20) UNIQUE NOT NULL,
    project_id INTEGER REFERENCES projects(id),
    vendor_id INTEGER REFERENCES vendors(id),
    process_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    base_amount DECIMAL(12,2) NOT NULL,
    difficulty_rate DECIMAL(3,2) DEFAULT 1.0,
    urgency_rate DECIMAL(3,2) DEFAULT 1.0,
    adjusted_amount DECIMAL(12,2) NOT NULL,
    vat_amount DECIMAL(12,2) NOT NULL,
    withholding_tax DECIMAL(12,2) DEFAULT 0,
    net_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    ordered_by INTEGER REFERENCES users(id),
    approved_by INTEGER REFERENCES users(id),
    ordered_at TIMESTAMP,
    approved_at TIMESTAMP,
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Settlements Table (CRITICAL)
CREATE TABLE settlements (
    id SERIAL PRIMARY KEY,
    settlement_no VARCHAR(20) UNIQUE NOT NULL,
    order_id INTEGER REFERENCES purchase_orders(id),
    vendor_id INTEGER REFERENCES vendors(id),
    project_id INTEGER REFERENCES projects(id),
    completed_cuts INTEGER NOT NULL,
    base_amount DECIMAL(12,2) NOT NULL,
    vat_amount DECIMAL(12,2) NOT NULL,
    withholding_tax DECIMAL(12,2) DEFAULT 0,
    net_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_date DATE,
    settled_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add 9 more tables: episodes, cuts, vendors, qc_reviews, 
-- notifications, audit_logs, contracts, files, etc.
```

#### Implementation Steps
1. **Install PostgreSQL 15+** (Day 1)
   ```bash
   sudo apt-get install postgresql-15
   sudo systemctl start postgresql
   ```

2. **Create database and user** (Day 1)
   ```sql
   CREATE DATABASE recess_ims;
   CREATE USER recess_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE recess_ims TO recess_user;
   ```

3. **Implement schema** (Day 2-3)
   - Create all 14 tables
   - Add foreign keys
   - Create indexes
   - Set up constraints

4. **Create migrations** (Day 3-4)
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

5. **Import seed data** (Day 5)
   - Convert JSON to SQL inserts
   - Load test data
   - Verify relationships

#### Estimated Effort
- **Timeline:** 1 week
- **Cost:** $3,000-5,000 USD

---

### Issue #3: Frontend-Backend Not Connected
**Status:** ❌ NOT STARTED  
**Priority:** P0 - CRITICAL  
**Blocking:** System functionality

#### Problem
Frontend code uses static file fetches:
```javascript
// Current (Broken)
const response = await fetch('../data/projects.json');
const projects = await response.json();

// No error handling
// No loading states
// No authentication headers
// No API base URL configuration
```

#### Impact
- Frontend cannot communicate with backend
- All data is static
- No dynamic updates
- Cannot save changes

#### Solution Required
```javascript
// Required API Configuration
// frontend/config/api.js
const API_CONFIG = {
  baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// API Client Utility
class APIClient {
  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.token = localStorage.getItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      ...API_CONFIG.headers,
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Request Failed:', error);
      throw error;
    }
  }

  // GET request
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Usage Example
const api = new APIClient();

// Load projects dynamically
async function loadProjects() {
  try {
    showLoading();
    const projects = await api.get('/projects');
    renderProjects(projects);
  } catch (error) {
    showError('Failed to load projects');
  } finally {
    hideLoading();
  }
}

// Create purchase order
async function createOrder(orderData) {
  try {
    const order = await api.post('/orders', orderData);
    showSuccess('Order created successfully');
    return order;
  } catch (error) {
    showError('Failed to create order');
  }
}
```

#### Files to Update (Priority Order)
1. **Authentication Pages** (URGENT)
   - `app/login.html` - Connect to POST /api/v1/auth/login
   - `app/signup.html` - Connect to POST /api/v1/auth/register

2. **Order Management** (CRITICAL)
   - `app/pages/accounting/order-create-v2.html` - POST /api/v1/orders
   - `app/pages/accounting/purchase-order.html` - GET /api/v1/orders
   
3. **Settlement Pages** (CRITICAL)
   - `app/pages/settlement/settlement-process.html` - POST /api/v1/settlements
   - `app/pages/settlement/settlement-dashboard.html` - GET /api/v1/settlements/summary

4. **Production Pages** (HIGH)
   - `app/pages/production/project-dashboard.html` - GET /api/v1/projects
   - `app/pages/production/pre-production.html` - GET /api/v1/episodes

5. **All Other Pages** (Medium-Low)
   - Update remaining 165+ pages

#### Implementation Steps
1. **Create API utility** (Day 1)
   - Implement APIClient class
   - Add error handling
   - Add loading states

2. **Update authentication** (Day 2-3)
   - Connect login page
   - Store JWT tokens
   - Add token refresh logic

3. **Update core pages** (Week 2)
   - Order creation/management
   - Settlement processing
   - Project dashboard

4. **Update all pages** (Week 3)
   - Remaining 165+ pages
   - Add error states
   - Add loading indicators

5. **Testing** (Week 4)
   - End-to-end tests
   - Error scenario testing
   - Performance testing

#### Estimated Effort
- **Timeline:** 3-4 weeks
- **Cost:** $8,000-12,000 USD

---

## ⚠️ HIGH PRIORITY ISSUES

### Issue #4: No Authentication System
**Status:** ❌ NOT STARTED  
**Priority:** P1 - HIGH  
**Impact:** Security risk

#### Problem
- Login page is non-functional
- No password hashing
- No JWT tokens
- LocalStorage used for fake sessions
- No role-based access control

#### Solution
```python
# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify user credentials
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role_level,
            "tier": user.tier
        }
    }
```

#### Estimated Effort
- **Timeline:** 1 week
- **Cost:** $3,000-5,000 USD

---

### Issue #5: No File Storage System
**Status:** ❌ NOT STARTED  
**Priority:** P1 - HIGH  
**Impact:** Cannot upload work files

#### Problem
- File upload UI exists but not functional
- No storage backend (S3/MinIO)
- Cannot attach files to orders
- Cannot store work deliverables

#### Solution Options

**Option A: MinIO (Self-hosted, Recommended for MVP)**
```python
# Pros: Free, S3-compatible, self-hosted
# Cons: Need to manage infrastructure

from minio import Minio

client = Minio(
    "minio.example.com:9000",
    access_key="ACCESS_KEY",
    secret_key="SECRET_KEY",
    secure=True
)

@router.post("/upload")
async def upload_file(file: UploadFile):
    client.put_object(
        "recess-files",
        file.filename,
        file.file,
        file.size
    )
    return {"url": f"https://minio.example.com/recess-files/{file.filename}"}
```

**Option B: AWS S3 (Cloud, Production)**
```python
# Pros: Managed, scalable, CDN integration
# Cons: Costs money

import boto3

s3_client = boto3.client('s3')

@router.post("/upload")
async def upload_file(file: UploadFile):
    s3_client.upload_fileobj(
        file.file,
        "recess-ims-bucket",
        file.filename
    )
    url = f"https://recess-ims-bucket.s3.amazonaws.com/{file.filename}"
    return {"url": url}
```

#### Estimated Effort
- **Timeline:** 3-5 days
- **Cost:** $2,000-3,000 USD + hosting

---

### Issue #6: No QC Workflow Automation
**Status:** ❌ NOT STARTED  
**Priority:** P1 - HIGH  
**Impact:** Manual QC process

#### Problem
- QC approval buttons exist but don't work
- No status tracking
- No notification on status change
- No escalation logic

#### Solution
```python
# backend/app/services/qc_service.py

class QCService:
    async def submit_for_qc1(self, cut_id: int, user_id: int):
        """Worker submits cut for Team Lead review (QC1)"""
        cut = await get_cut(cut_id)
        
        # Validate cut has required files
        if not cut.files:
            raise ValueError("Cannot submit: No files attached")
        
        # Update status
        cut.status = "qc1_pending"
        cut.submitted_at = datetime.utcnow()
        cut.submitted_by = user_id
        await update_cut(cut)
        
        # Notify Team Lead
        team_lead = await get_team_lead(cut.assigned_team)
        await send_notification(
            user_id=team_lead.id,
            message=f"Cut {cut.cut_no} ready for QC1 review"
        )
        
    async def approve_qc1(self, cut_id: int, reviewer_id: int):
        """Team Lead approves QC1"""
        reviewer = await get_user(reviewer_id)
        
        # Check permission
        if reviewer.role_level != 6:  # L6 = Team Lead
            raise PermissionError("Only Team Leads can approve QC1")
        
        cut = await get_cut(cut_id)
        cut.qc1_status = "approved"
        cut.qc1_approved_by = reviewer_id
        cut.qc1_approved_at = datetime.utcnow()
        cut.status = "qc2_pending"
        await update_cut(cut)
        
        # Notify PM for QC2
        pm = await get_pm(cut.project_id)
        await send_notification(
            user_id=pm.id,
            message=f"Cut {cut.cut_no} passed QC1, needs QC2 review"
        )
        
    async def reject_qc1(self, cut_id: int, reviewer_id: int, reason: str):
        """Team Lead rejects QC1 (rework needed)"""
        cut = await get_cut(cut_id)
        cut.qc1_status = "rejected"
        cut.qc1_rejected_by = reviewer_id
        cut.qc1_rejection_reason = reason
        cut.status = "rework"
        await update_cut(cut)
        
        # Notify worker
        await send_notification(
            user_id=cut.assigned_to,
            message=f"Cut {cut.cut_no} needs rework: {reason}"
        )
```

#### Estimated Effort
- **Timeline:** 1 week
- **Cost:** $3,000-5,000 USD

---

## 📊 MEDIUM PRIORITY ISSUES

### Issue #7: No Real-time Updates
**Status:** NOT STARTED  
**Priority:** P2 - MEDIUM  

#### Problem
- Dashboard shows static data
- No live progress updates
- Users must refresh to see changes

#### Solution
- Implement WebSocket connections
- Add Server-Sent Events (SSE)
- Real-time dashboard updates

#### Estimated Effort: 3-5 days

---

### Issue #8: No Notification System
**Status:** NOT STARTED  
**Priority:** P2 - MEDIUM  

#### Problem
- No email notifications
- No in-app notifications
- Users miss important updates

#### Solution
- Email service (SendGrid/AWS SES)
- In-app notification center
- Push notifications

#### Estimated Effort: 3-5 days

---

### Issue #9: No Export Functionality
**Status:** NOT STARTED  
**Priority:** P2 - MEDIUM  

#### Problem
- Excel export buttons don't work
- Cannot export reports
- Cannot print invoices

#### Solution
- Implement Excel generation (openpyxl)
- PDF generation (ReportLab)
- CSV exports

#### Estimated Effort: 2-3 days

---

## 📈 SUMMARY

### Total Issues: 9
- **Critical (P0):** 3 issues - BLOCKING ALL FUNCTIONALITY
- **High (P1):** 3 issues - BLOCKING KEY FEATURES
- **Medium (P2):** 3 issues - USABILITY PROBLEMS

### Total Effort Required
- **MVP (P0):** 8 weeks
- **Production-Ready (P0+P1):** 12 weeks
- **Feature-Complete (All):** 14 weeks

### Total Cost Estimate
- **MVP:** $26,000-40,000 USD
- **Production:** $40,000-60,000 USD
- **Complete:** $50,000-75,000 USD

### Immediate Next Steps
1. ✅ **Hire backend developer** (FastAPI expert)
2. ✅ **Set up PostgreSQL database**
3. ✅ **Implement authentication API**
4. ✅ **Build core APIs (orders, settlements)**
5. ✅ **Connect frontend to backend**

---

**Status:** WAITING FOR DEVELOPMENT TO START  
**Blocking:** Backend team assignment  
**Next Review:** After MVP completion (Week 4)
