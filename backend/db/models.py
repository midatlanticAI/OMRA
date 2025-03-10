"""
Database models for the OpenManus Appliance Repair Business Automation System
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, DateTime, ForeignKey, JSON, Enum as SQLAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from backend.core.encryption import EncryptedType

Base = declarative_base()

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class StatusEnum(str, Enum):
    pending = "pending"
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    _email = Column('email', String(255), unique=True, nullable=False)
    _phone = Column('phone', String(20))
    _address_line1 = Column('address_line1', String(255))
    _address_line2 = Column('address_line2', String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appliances = relationship("Appliance", back_populates="customer")
    service_requests = relationship("ServiceRequest", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    
    # Integration fields
    ghl_contact_id = Column(String(100))
    kickserv_customer_id = Column(String(100))
    
    # Encrypted fields with hybrid properties
    @hybrid_property
    def email(self):
        return EncryptedType.decrypt_value(self._email)
    
    @email.setter
    def email(self, value):
        self._email = EncryptedType.encrypt_value(value)
    
    @hybrid_property
    def phone(self):
        return EncryptedType.decrypt_value(self._phone)
    
    @phone.setter
    def phone(self, value):
        self._phone = EncryptedType.encrypt_value(value)
    
    @hybrid_property
    def address_line1(self):
        return EncryptedType.decrypt_value(self._address_line1)
    
    @address_line1.setter
    def address_line1(self, value):
        self._address_line1 = EncryptedType.encrypt_value(value)
    
    @hybrid_property
    def address_line2(self):
        return EncryptedType.decrypt_value(self._address_line2)
    
    @address_line2.setter
    def address_line2(self, value):
        self._address_line2 = EncryptedType.encrypt_value(value)
    
    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name}>"

class Appliance(Base):
    """Appliance model"""
    __tablename__ = "appliances"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    type = Column(String(50), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    purchase_date = Column(Date)
    warranty_expiration = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="appliances")
    service_requests = relationship("ServiceRequest", back_populates="appliance")
    
    def __repr__(self):
        return f"<Appliance {self.type} {self.brand} {self.model}>"

class ServiceRequest(Base):
    """Service Request model"""
    __tablename__ = "service_requests"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    appliance_id = Column(Integer, ForeignKey("appliances.id"))
    status = Column(SQLAEnum(StatusEnum), nullable=False, default=StatusEnum.pending)
    priority = Column(SQLAEnum(PriorityEnum), nullable=False, default=PriorityEnum.medium)
    issue_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="service_requests")
    appliance = relationship("Appliance", back_populates="service_requests")
    appointments = relationship("Appointment", back_populates="service_request")
    parts_used = relationship("PartsUsed", back_populates="service_request")
    invoices = relationship("Invoice", back_populates="service_request")
    
    # Integration fields
    kickserv_job_id = Column(String(100))
    
    def __repr__(self):
        return f"<ServiceRequest {self.id} - {self.status.value}>"

class Technician(Base):
    """Technician model"""
    __tablename__ = "technicians"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    specializations = Column(JSON)  # Array of specializations
    availability_schedule = Column(JSON)  # JSON representation of availability
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="technician")
    
    def __repr__(self):
        return f"<Technician {self.first_name} {self.last_name}>"

class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(SQLAEnum(StatusEnum), nullable=False, default=StatusEnum.pending)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="appointments")
    technician = relationship("Technician", back_populates="appointments")
    
    # Integration fields
    ghl_appointment_id = Column(String(100))
    kickserv_appointment_id = Column(String(100))
    
    def __repr__(self):
        return f"<Appointment {self.id} - {self.start_time}>"

class Invoice(Base):
    """Invoice model"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    issued_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_method = Column(String(50))
    payment_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    
    def __repr__(self):
        return f"<Invoice {self.id} - ${self.total_amount}>"

class Part(Base):
    """Part model"""
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    part_number = Column(String(100), unique=True, nullable=False)
    compatible_appliances = Column(JSON)  # Array of compatible appliance types
    cost = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    inventory_count = Column(Integer, nullable=False)
    reorder_threshold = Column(Integer, nullable=False)
    supplier = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parts_used = relationship("PartsUsed", back_populates="part")
    
    def __repr__(self):
        return f"<Part {self.name} - {self.part_number}>"

class PartsUsed(Base):
    """Parts Used model"""
    __tablename__ = "parts_used"
    
    id = Column(Integer, primary_key=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))
    part_id = Column(Integer, ForeignKey("parts.id"))
    quantity = Column(Integer, nullable=False)
    price_charged = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="parts_used")
    part = relationship("Part", back_populates="parts_used")
    
    def __repr__(self):
        return f"<PartsUsed {self.part_id} - {self.quantity}>"

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    _email = Column('email', String(255), unique=True, nullable=False)
    _full_name = Column('full_name', String(100))
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Encrypted fields with hybrid properties
    @hybrid_property
    def email(self):
        return EncryptedType.decrypt_value(self._email)
    
    @email.setter
    def email(self, value):
        self._email = EncryptedType.encrypt_value(value)
    
    @hybrid_property
    def full_name(self):
        return EncryptedType.decrypt_value(self._full_name)
    
    @full_name.setter
    def full_name(self, value):
        self._full_name = EncryptedType.encrypt_value(value)
    
    def __repr__(self):
        return f"<User {self.username}>"

class APIKey(Base):
    """API Key model for authentication"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    def __repr__(self):
        return f"<APIKey {self.name}>" 