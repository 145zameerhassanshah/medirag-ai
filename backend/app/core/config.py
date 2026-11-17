"""Runtime environment settings. Keep secrets in backend/.env, never commit them."""
from pathlib import Path
import os
from dotenv import load_dotenv
BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./medirag.db')
JWT_SECRET = os.getenv('JWT_SECRET', '')
if len(JWT_SECRET) < 32:
    raise RuntimeError('Set JWT_SECRET (32+ random characters) in backend/.env')
