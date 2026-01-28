"""
Database Configuration Module

This module handles the database connection setup using SQLAlchemy.
It loads environment variables for configuration and creates the database engine
and session factory used throughout the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Retrieve the database URL from environment variables
# Format: postgresql://[user]:[password]@[postgresserverhost]:[port]/[database_name]
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:admin@localhost:5432/contact_book_database"

print(f"--- DATABASE CONNECTION ATTEMPT ---")
print(f"Target: {SQLALCHEMY_DATABASE_URL}")
print(f"------------------------------------")

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from the .env file.")

# Create the SQLAlchemy engine which manages the connection pool
# Note: connect_args={'check_same_thread': False} is not needed for PostgreSQL, only for SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a customized Session class for database interactions
# autocommit=False: We manually commit to ensure transaction integrity
# autoflush=False: We manually flush changes to the DB
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Base class for our ORM models; all models will inherit from this
Base = declarative_base()