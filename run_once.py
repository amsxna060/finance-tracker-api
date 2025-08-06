import sys
import os
from database.connection import create_tables
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    create_tables()  # Run this once manually