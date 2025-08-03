# JWT Authentication Implementation Guide

## 🎯 Step-by-Step Implementation Plan

This guide provides practical implementation steps for adding JWT authentication to the FastAPI finance tracker, building on the current codebase analysis.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- ✅ Current codebase running (`fastapi dev main.py`)
- ✅ Dependencies installed (python-jose, passlib already available)
- ✅ Basic understanding of JWT concepts
- ✅ Test client ready (curl, Postman, or httpx)

---

## 🛠️ Step 1: Environment Setup (5 minutes)

### 1.1 Create Environment Variables
Create a `.env` file in the project root:

```env
# .env
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 1.2 Update .gitignore
Ensure `.env` is in your `.gitignore`:
```gitignore
.env
__pycache__/
*.pyc
.venv/
```

### 1.3 Load Environment Variables
Update `main.py` to load environment variables:
```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

---

## 🔧 Step 2: Create JWT Utilities (15 minutes)

### 2.1 Update util.py with JWT Functions
Add these functions to `util.py`:

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing the payload data (usually user info)
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Could not validate credentials")
```

### 2.2 Test JWT Functions
Create a simple test script (`test_jwt.py`):
```python
from util import create_access_token, verify_token

# Test token creation and verification
test_data = {"sub": "test@example.com", "user_id": 1}
token = create_access_token(test_data)
print(f"Generated token: {token}")

decoded = verify_token(token)
print(f"Decoded payload: {decoded}")
```

---

## 📝 Step 3: Create Login Models (10 minutes)

### 3.1 Create LoginRequest Model
Create `Models/LoginRequest.py`:

```python
from pydantic import BaseModel, field_validator

class LoginRequest(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    def email_validation(cls, email):
        if '@' not in email:
            raise ValueError("Invalid email format")
        return email.lower().strip()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds
```

### 3.2 Update Models/__init__.py
```python
from .User import User
from .UserCreate import UserCreate
from .LoginRequest import LoginRequest, TokenResponse
```

---

## 🔐 Step 4: Implement Authentication Dependencies (20 minutes)

### 4.1 Create Authentication Dependencies
Add to `main.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from Models.LoginRequest import LoginRequest, TokenResponse
from util import verify_token

# Security scheme for JWT
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Extract and validate JWT token, return current user.
    
    This dependency can be used to protect routes that require authentication.
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Find user in fake_users_db
    user = None
    for u in fake_users_db:
        if u.email == email and u.id == user_id:
            user = u
            break
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Get current user and check if they're active/verified.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

---

## 🚪 Step 5: Implement Login Endpoint (25 minutes)

### 5.1 Add Login Endpoint to main.py
```python
@app.post('/login', response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return JWT token.
    """
    # Find user by email
    user = None
    for u in fake_users_db:
        if u.email.lower() == login_data.email.lower():
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

---

## 🛡️ Step 6: Protect Existing Endpoints (15 minutes)

### 6.1 Update /user/me Endpoint
Replace the hardcoded `/user/me` endpoint:

```python
@app.get("/user/me")
async def get_user_me(current_user = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    """
    # Return user data without password
    user_data = current_user.model_dump()
    user_data["password"] = "********"  # Hide password
    return user_data
```

### 6.2 Create Additional Protected Endpoints
```python
@app.get("/user/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    """
    Get detailed user profile (protected endpoint).
    """
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "currency": current_user.currency,
        "location": current_user.location,
        "member_since": current_user.date_created
    }

@app.put("/user/profile")
async def update_user_profile(
    update_data: dict,
    current_user = Depends(get_current_user)
):
    """
    Update user profile (protected endpoint).
    """
    # In a real app, you'd update the database
    return {
        "message": "Profile updated successfully",
        "user_id": current_user.id
    }
```

---

## 🧪 Step 7: Test the Implementation (20 minutes)

### 7.1 Manual Testing Script
Create `test_auth_flow.py`:

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_registration():
    """Test user registration"""
    user_data = {
        "name": "JWT Test User",
        "email": "jwttest@example.com",
        "age": 28,
        "gender": "F",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"Registration: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_login():
    """Test user login"""
    login_data = {
        "email": "jwttest@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(json.dumps(token_data, indent=2))
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/user/me", headers=headers)
    print(f"Protected endpoint: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    response = requests.get(f"{BASE_URL}/user/me")
    print(f"Unauthorized access: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    print("=== Testing Authentication Flow ===")
    
    # Test registration
    test_registration()
    print("\n" + "="*50 + "\n")
    
    # Test login
    token = test_login()
    print("\n" + "="*50 + "\n")
    
    if token:
        # Test protected endpoint with token
        test_protected_endpoint(token)
        print("\n" + "="*50 + "\n")
    
    # Test unauthorized access
    test_unauthorized_access()
```

### 7.2 Run Tests
```bash
# Start server
fastapi dev main.py

# In another terminal
python test_auth_flow.py
```

### 7.3 Expected Test Results
1. **Registration**: 200 OK with user data
2. **Login**: 200 OK with JWT token
3. **Protected endpoint with token**: 200 OK with user data
4. **Protected endpoint without token**: 401 Unauthorized

---

## 🔍 Step 8: Verification and Debugging (10 minutes)

### 8.1 Common Issues and Solutions

**Issue: "Could not validate credentials"**
- Check SECRET_KEY is set correctly
- Verify token format in Authorization header
- Ensure token hasn't expired

**Issue: "User not found after token validation"**
- Check user exists in fake_users_db
- Verify email matching logic (case sensitivity)

**Issue: "Invalid token format"**
- Ensure Authorization header format: `Bearer <token>`
- Check for extra spaces or characters

### 8.2 Debug Helper Endpoint
Add a debug endpoint to inspect tokens:

```python
@app.post("/debug/token")
async def debug_token(token: str):
    """Debug endpoint to inspect JWT token contents"""
    try:
        payload = verify_token(token)
        return {"valid": True, "payload": payload}
    except JWTError as e:
        return {"valid": False, "error": str(e)}
```

---

## 🎉 Step 9: Validate Complete Implementation

### 9.1 Final Checklist
- ✅ Environment variables configured
- ✅ JWT utilities implemented
- ✅ Login endpoint working
- ✅ Authentication dependencies created
- ✅ Protected endpoints require valid tokens
- ✅ Error handling for invalid tokens
- ✅ Manual testing successful

### 9.2 API Documentation
Check your API docs at `http://127.0.0.1:8000/docs`:
- Login endpoint should be visible
- Protected endpoints should show security requirements
- Test directly in Swagger UI

---

## 🚀 Next Steps

After successful JWT implementation:

1. **Add Role-Based Access Control**
   - Admin vs User roles
   - Different permission levels

2. **Implement Token Refresh**
   - Refresh tokens for extended sessions
   - Token blacklisting

3. **Database Integration**
   - Replace fake_users_db with SQLAlchemy
   - Persistent user storage

4. **Enhanced Security**
   - Rate limiting for login attempts
   - Password complexity requirements
   - Email verification

5. **Testing Suite**
   - Unit tests for authentication
   - Integration tests for protected endpoints

---

## 📚 Learning Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io Debugger](https://jwt.io/)
- [OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

**Congratulations! You now have a secure JWT authentication system! 🎊**