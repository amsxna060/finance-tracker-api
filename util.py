from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta


# JWT Configuration
SECRET_KEY = "your-secret-key-here-make-it-strong"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing Setup ---
# We use bcrypt as it's a strong, widely-used hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    
    Args:
        plain_password: The password to verify.
        hashed_password: The stored hash to compare against.
        
    Returns:
        True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    
    Args:
        password: The password to hash.
        
    Returns:
        The hashed password string.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a JWT access token.
    
    Args:
        data: The data to encode in the token (usually user info)
        expires_delta: How long the token should be valid
        
    Returns:
        The encoded JWT token string
    """
    # Coping data so we don't modify orgincal data
    to_encode = data.copy()

    # Step 2 for expiration time

    if expires_delta : 
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    #Add expiration time into data
    to_encode.update({"exp":expire})

    # Generate JWT token
    jwt_token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    
    # Return the token
    return jwt_token

def verify_token(token: str):
    """
    Verifies and decodes a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        The decoded data if valid, None if invalid
    """
    # Decode the token
    try : 
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        return payload
    except : 
        # If Token is valid, tempored or have expired.
        return None