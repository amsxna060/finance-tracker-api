from passlib.context import CryptContext

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