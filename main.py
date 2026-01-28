"""
Main Application Entry Point

This module initializes the FastAPI application, sets up the database tables,
and includes the API routers. It serves as the root of the application backend.
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
import model
from databse import engine
from routers import contacts, auth, admin

# Initialize the FastAPI application instance
app = FastAPI()

# Create all database tables defined in the models
# This checks the metadata and creates tables if they don't exist
model.Base.metadata.create_all(bind=engine)

# Register routers to handle requests for different resources
app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(admin.router)
