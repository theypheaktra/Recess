# RECESS IMS Backend API

FastAPI backend for RECESS IMS (Reliable Entertainment Contents Settlement System)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+

### Installation

1. **Install PostgreSQL** (if not installed):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-15

# macOS
brew install postgresql@15

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS
```

2. **Create Database**:
```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE recess_ims;
CREATE USER recess_user WITH PASSWORD 'recess_password';
GRANT ALL PRIVILEGES ON DATABASE recess_ims TO recess_user;
\q
```

3. **Install Python Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env if needed (database URL, JWT secret, etc.)
```

5. **Initialize Database**:
```bash
python init_db.py
```

6. **Start API Server**:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 Test Accounts

After running `init_db.py`, these test accounts are available:

| Role | Email | Password | Tier | Level |
|------|-------|----------|------|-------|
| Committee Chairman | chairman@tbc-committee.jp | password123 | 0 | L0 |
| **Producer/PD** | **pd@recess-studio.jp** | **password123** | **1** | **L3** |
| Desk | desk@recess-studio.jp | password123 | 1 | L4 |
| Sub PM | pm@seoul-anim.kr | password123 | 2 | L5 |
| Team Lead | lead@seoul-anim.kr | password123 | 2 | L6 |
| Worker | worker@example.com | password123 | 2 | L7 |

**Recommended for testing:** Use `pd@recess-studio.jp` (has full permissions)

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (returns JWT tokens)
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout

### Purchase Orders ⭐ CORE
- `POST /api/v1/orders` - Create purchase order
- `GET /api/v1/orders` - List orders (with filters)
- `GET /api/v1/orders/{id}` - Get order details
- `PUT /api/v1/orders/{id}` - Update order
- `POST /api/v1/orders/{id}/approve` - Approve order
- `POST /api/v1/orders/{id}/cancel` - Cancel order
- `POST /api/v1/orders/calculate` - Calculate amounts (preview)

### Settlements ⭐ CORE
- `POST /api/v1/settlements` - Create settlement
- `GET /api/v1/settlements` - List settlements (with filters)
- `GET /api/v1/settlements/{id}` - Get settlement details
- `PUT /api/v1/settlements/{id}` - Update settlement
- `POST /api/v1/settlements/{id}/complete` - Complete settlement (mark as paid)
- `GET /api/v1/settlements/summary` - Get summary statistics

## 💰 Business Logic

### Purchase Order Calculation

```python
# Formula
base_amount = quantity × unit_price
adjusted_amount = base_amount × difficulty_rate × urgency_rate
vat_amount = adjusted_amount × 0.10  # 10% VAT
withholding_tax = adjusted_amount × 0.033  # 3.3% for freelancers
net_amount = adjusted_amount + vat_amount - withholding_tax
```

### Example Calculation

```
Quantity: 50 cuts
Unit Price: ¥15,000/cut
Difficulty Rate: 1.2 (20% increase)
Urgency Rate: 1.0 (no rush)
Withholding Rate: 3.3% (freelancer)

Base Amount: 50 × 15,000 = ¥750,000
Adjusted: 750,000 × 1.2 × 1.0 = ¥900,000
VAT (10%): 900,000 × 0.10 = ¥90,000
Withholding (3.3%): 900,000 × 0.033 = ¥29,700
Net Payment: 900,000 + 90,000 - 29,700 = ¥960,300
```

## 🗄️ Database Schema

### Core Tables
- `users` - User accounts (authentication & profiles)
- `organizations` - Companies and studios
- `vendors` - Subcontractors and freelancers
- `projects` - Animation projects
- `episodes` - Episodes within projects
- `cuts` - Individual animation cuts
- `purchase_orders` ⭐ - Work orders with pricing
- `settlements` ⭐ - Payment processing

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Login with test account:
   - Username: `pd@recess-studio.jp`
   - Password: `password123`
4. Copy the access_token
5. Paste in the Authorize dialog
6. Now you can test all endpoints

### Using curl

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=pd@recess-studio.jp&password=password123"

# Response: {"access_token": "...", "refresh_token": "...", ...}

# 2. Use the token for authenticated requests
TOKEN="your-access-token-here"

# Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# Create purchase order
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "vendor_id": 1,
    "process_type": "layout",
    "quantity": 50,
    "unit_price": 15000,
    "difficulty_rate": 1.2,
    "withholding_tax_rate": 0.033
  }'

# List orders
curl -X GET "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer $TOKEN"

# Calculate order (preview)
curl -X POST "http://localhost:8000/api/v1/orders/calculate?quantity=50&unit_price=15000&difficulty_rate=1.2&withholding_tax_rate=0.033" \
  -H "Authorization: Bearer $TOKEN"
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   └── security.py        # JWT & password hashing
│   ├── models/
│   │   ├── user.py            # User model
│   │   ├── organization.py    # Organization model
│   │   ├── project.py         # Project/Episode/Cut models
│   │   ├── vendor.py          # Vendor model
│   │   ├── purchase_order.py  # Purchase order model ⭐
│   │   └── settlement.py      # Settlement model ⭐
│   ├── schemas/
│   │   ├── user.py            # User Pydantic schemas
│   │   ├── purchase_order.py  # Order Pydantic schemas
│   │   └── settlement.py      # Settlement Pydantic schemas
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── purchase_orders.py # Order management endpoints ⭐
│   │   └── settlements.py     # Settlement endpoints ⭐
│   └── main.py                # FastAPI application
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
└── .env.example               # Environment variables template
```

## 🔐 Security

- **Password Hashing**: bcrypt
- **JWT Tokens**: RS256 algorithm
- **Access Token**: 30 minutes expiry
- **Refresh Token**: 7 days expiry
- **CORS**: Configured for localhost development

## 🚀 Deployment

For production deployment:

1. Change `SECRET_KEY` in `.env` to a strong random string
2. Use a production-grade PostgreSQL instance
3. Set `ENVIRONMENT=production` in `.env`
4. Use a reverse proxy (Nginx) with HTTPS
5. Consider using Gunicorn/uvicorn workers:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 📝 API Documentation

Full API documentation is available at:
- Interactive: http://localhost:8000/docs (Swagger UI)
- Alternative: http://localhost:8000/redoc (ReDoc)

## 🐛 Troubleshooting

### Database Connection Error
```
FATAL: password authentication failed for user "recess_user"
```
**Solution**: Check your PostgreSQL password and DATABASE_URL in `.env`

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Port Already in Use
```
ERROR: [Errno 48] Address already in use
```
**Solution**: Change port or kill existing process:
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

## 📞 Support

For issues or questions, refer to:
- Main documentation: `/docs` folder
- API documentation: http://localhost:8000/docs
- Project repository: GitHub

---

**Status:** ✅ MVP Backend Complete  
**Version:** 3.0.0  
**Last Updated:** 2026-02-10
