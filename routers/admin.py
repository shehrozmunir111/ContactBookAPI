"""
Admin Router

This module provides administrative endpoints for system oversight.
It handles authorized access to global statistics and user management data.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from databse import SessionLocal
from model import Contacts, Users

from typing import Annotated
from routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/stats")
async def read_admin_stats(db: db_dependency, user: user_dependency):
    """
    Retrieve System Statistics
    
    Provides an overview of the system for admin users, including:
    - Total number of users
    - Total number of contacts
    - Top 5 users by contact count
    
    Requires 'admin' role.
    """
    # Security Check: Ensure the user is an admin
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can see the details.")

    total_users = db.query(Users).count()
    total_contacts = db.query(Contacts).count()

    # Top 5 Users who has most contacts
    top_users = db.query(
        Users.username,
        func.count(Contacts.id).label("contact_count")
    ).join(Contacts, Users.id == Contacts.owner_id) \
     .group_by(Users.id) \
     .order_by(func.count(Contacts.id).desc()) \
     .limit(5).all()

    # convert Data into readable format
    formatted_top_users = [{"username": row[0], "count": row[1]} for row in top_users]

    return {
        "overview": {
            "total_users": total_users,
            "total_contacts": total_contacts
        },
        "top_performers": formatted_top_users
    }