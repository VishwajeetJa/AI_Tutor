# app/__init__.py

from .main import app

# This allows your application server to be run cleanly from the root directory 
# using: uvicorn app:app --reload
__all__ = ["app"]