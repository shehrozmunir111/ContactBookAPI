"""
Contacts Router

This module provides CRUD (Create, Read, Update, Delete) operations for contacts.
It enforces ownership permissions so users can only manage their own contacts,
while preventing duplicate phone numbers per user.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from databse import SessionLocal
from model import Contacts
from typing import Annotated, Optional, List
from sqlalchemy import or_

from routers.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
# User dependency setup
user_dependency = Annotated[dict, Depends(get_current_user)]

class ContactRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    phone_number: str = Field(pattern=r"^\+92\d{10}$")
    # Email: Optional, but must be valid if provided
    email: Optional[EmailStr] = None

class ContactResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    email: Optional[EmailStr] = None
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        # This tells Pydantic to read data even if it's not a dict (e.g., an ORM model)
        from_attributes = True


@router.get("/", response_model=List[ContactResponse])
async def read_all_contacts(
        db: db_dependency,
        user: user_dependency,
        search: Optional[str] = None,
        limit: int = 10,  # Default to 10 contacts per page
        offset: int = 0  # Default to start at the beginning
):
    """
    Retrieve All Contacts.

    Fetches a list of contacts belonging to the authenticated user.
    Supports search filtering (name/phone) and pagination.

    Args:
        search (str, optional): Search term for filtering.
        limit (int): Number of records to return.
        offset (int): Number of records to skip.

    Returns:
        List[ContactResponse]: List of contact objects.
    """
    # 1. Base query: Only get contacts belonging to the logged-in user
    query = db.query(Contacts).filter(Contacts.owner_id == user.get("id"))

    # 2. Search logic: Filter by Name or Phone Number if search is provided
    if search:
        query = query.filter(
            or_(
                Contacts.name.icontains(search),
                Contacts.phone_number.contains(search)
            )
        )

    # 3. Pagination logic: Apply offset first, then limit
    # This ensures we skip the previous pages and take only the next 'limit' amount
    contacts = query.offset(offset).limit(limit).all()

    return contacts

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(db: db_dependency, contact_request: ContactRequest, user: user_dependency):
    """
    Create a New Contact.

    Adds a new contact to the user's address book.
    Ensures the phone number is unique for this specific user.

    Args:
        contact_request (ContactRequest): The new contact data.

    Returns:
        ContactResponse: The created contact object.

    Raises:
        HTTPException: If the phone number already exists for this user.
    """
    # 1. Check if the phone number already exists FOR THIS USER
    existing_contact = db.query(Contacts).filter(
        Contacts.owner_id == user.get('id'),
        Contacts.phone_number == contact_request.phone_number
    ).first()

    if existing_contact:
        raise HTTPException(
            status_code=400,
            detail="This contact number is already saved."
        )
    # 2. Proceed with creation if check passes
    contact_model = Contacts(**contact_request.model_dump(), owner_id=user.get("id"))
    db.add(contact_model)
    db.commit()
    db.refresh(contact_model)
    return contact_model


@router.put("/{contact_id}", response_model=ContactResponse,)
async def update_contact(db: db_dependency, contact_request: ContactRequest, user: user_dependency,
                         contact_id: int = Path(gt=0)):
    """
    Update an Existing Contact.

    Modifies details of a specific contact.
    Admins can update any contact; users can only update their own.

    Args:
        contact_id (int): ID of the contact to update.
        contact_request (ContactRequest): Updated data.

    Returns:
        ContactResponse: The updated contact object.
    
    Raises:
        HTTPException: If contact not found or permission denied.
    """
    query = db.query(Contacts).filter(Contacts.id == contact_id)

    # Allow admins to edit anything, but users only their own
    if user.get("role") != "admin":
        query = query.filter(Contacts.owner_id == user.get("id"))

    contact_model = query.first()

    if contact_model is None:
        raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found or you do not have permission to view it.")

    contact_model.name = contact_request.name
    contact_model.phone_number = contact_request.phone_number
    contact_model.email = contact_request.email

    db.add(contact_model)
    db.commit()
    db.refresh(contact_model)

    return contact_model


@router.delete("/{contact_id}")
async def delete_contact(db: db_dependency, user: user_dependency, contact_id: int = Path(gt=0)):
    """
    Delete a Contact.

    Removes a contact from the system.
    Restricted to Admins only in this implementation.

    Args:
        contact_id (int): ID of the contact to delete.

    Returns:
        dict: Success message.
    
    Raises:
        HTTPException: If user is not admin or contact not found.
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can delete the contact.")

    contact_model = db.query(Contacts).filter(Contacts.id == contact_id).first()

    if contact_model is None:
        raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found.")

    db.delete(contact_model)
    db.commit()

    return {"message": "Contact successfully deleted by Admin."}

