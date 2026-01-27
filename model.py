"""
Database Models Module

This module defines the SQLAlchemy ORM models representing the database schema.
It includes the Users and Contacts entities and their relationships.
"""
from databse import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Users(Base):
    """
    User Model
    
    Represents a registered user in the application.
    Stores authentication credentials and links to their contacts.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    # Username must be unique in the system
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Timestamp when the user was created
    created_at = Column(DateTime, server_default=func.now())
    
    # User role (e.g., 'user', 'admin')
    role = Column(String, default="user")

    # Relationship to Contacts: One User -> Many Contacts
    contacts = relationship("Contacts", back_populates="owner")


class Contacts(Base):
    """
    Contact Model
    
    Represents a contact entry (like an address book item).
    Each contact belongs to a specific User.
    """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, index=True)
    phone_number = Column(String)
    email = Column(String)
    
    # Track when the contact was first created
    # server_default=func.now() lets the DB set the time on insert
    created_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Track when the contact was last modified
    # onupdate=func.now() updates this field automatically on record update
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Foreign Key linking to the User model's id
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship to Users: Many Contacts -> One User
    owner = relationship("Users", back_populates="contacts")