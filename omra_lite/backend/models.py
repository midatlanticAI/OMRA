"""
Data Models for OMRA Lite

These Pydantic models define the data structures used in the application.
"""
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Annotated, ClassVar
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict, BeforeValidator

# Helper for MongoDB ObjectId handling - updated for Pydantic v2
def validate_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        try:
            ObjectId(v)  # Validate the ObjectId format
            return v
        except Exception:
            raise ValueError('Invalid ObjectId format')
    raise TypeError('ObjectId required')

PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

# Authentication and User Models
from auth_models import Token, TokenData

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: bool = False

class User(UserBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c85",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "disabled": False,
                "is_admin": False,
                "created_at": "2023-06-01T12:00:00"
            }
        }
    )

class UserInDB(User):
    hashed_password: str

class UserCreate(UserBase):
    password: str

# CRM Models
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_contact: str = "phone"  # phone, email

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    contact_info: ContactInfo
    address: Optional[Address] = None
    notes: Optional[str] = None

class Customer(CustomerBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c85",
                "first_name": "John",
                "last_name": "Doe",
                "contact_info": {
                    "phone": "555-123-4567",
                    "email": "john.doe@example.com",
                    "preferred_contact": "phone"
                },
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip_code": "12345",
                    "country": "USA"
                },
                "notes": "Prefers afternoon appointments",
                "created_at": "2023-06-01T12:00:00",
                "updated_at": "2023-06-01T12:00:00"
            }
        }
    )

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_info: Optional[ContactInfo] = None
    address: Optional[Address] = None
    notes: Optional[str] = None

# Service Models
class ServiceStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ServicePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ApplianceType(str, Enum):
    REFRIGERATOR = "refrigerator"
    WASHER = "washer"
    DRYER = "dryer"
    DISHWASHER = "dishwasher"
    STOVE = "stove"
    OVEN = "oven"
    MICROWAVE = "microwave"
    OTHER = "other"

class ServiceRequestBase(BaseModel):
    customer_id: str
    appliance_type: ApplianceType
    issue_description: str
    priority: ServicePriority = ServicePriority.MEDIUM
    scheduled_date: Optional[datetime] = None
    technician_id: Optional[str] = None
    notes: Optional[str] = None

class ServiceRequest(ServiceRequestBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    status: ServiceStatus = ServiceStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c85",
                "customer_id": "60d21b4967d0d8992e610c86",
                "appliance_type": "refrigerator",
                "issue_description": "Not cooling properly",
                "priority": "high",
                "status": "pending",
                "scheduled_date": "2023-06-15T09:00:00",
                "technician_id": "60d21b4967d0d8992e610c87",
                "notes": "Customer reports ice buildup in freezer",
                "created_at": "2023-06-01T12:00:00",
                "updated_at": "2023-06-01T12:00:00",
                "completed_at": None
            }
        }
    )

class ServiceRequestCreate(ServiceRequestBase):
    pass

class ServiceRequestUpdate(BaseModel):
    appliance_type: Optional[ApplianceType] = None
    issue_description: Optional[str] = None
    priority: Optional[ServicePriority] = None
    status: Optional[ServiceStatus] = None
    scheduled_date: Optional[datetime] = None
    technician_id: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

# Technician Models
class TechnicianBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    specialties: List[ApplianceType] = []
    active: bool = True

class Technician(TechnicianBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c87",
                "first_name": "Mike",
                "last_name": "Smith",
                "email": "mike.smith@example.com",
                "phone": "555-987-6543",
                "specialties": ["refrigerator", "washer", "dryer"],
                "active": True,
                "created_at": "2023-06-01T12:00:00",
                "updated_at": "2023-06-01T12:00:00"
            }
        }
    )

class TechnicianCreate(TechnicianBase):
    pass

class TechnicianUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialties: Optional[List[ApplianceType]] = None
    active: Optional[bool] = None

# Agent Models
class AgentType(str, Enum):
    CUSTOMER_SERVICE = "customer_service"
    DIAGNOSIS = "diagnosis"
    SCHEDULING = "scheduling"
    GENERAL = "general"
    SUPERVISOR = "supervisor"
    SPECIALIST = "specialist"
    RESEARCHER = "researcher"
    ASSISTANT = "assistant"

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TRAINING = "training"
    PENDING = "pending"

class AgentModel(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    LLAMA_2_7B = "llama-2-7b"
    LLAMA_2_13B = "llama-2-13b"
    LLAMA_2_70B = "llama-2-70b"
    MISTRAL_7B = "mistral-7b"
    CUSTOM = "custom"

class AgentCapability(str, Enum):
    REASONING = "reasoning"
    QA = "question_answering"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE_WRITING = "creative_writing"
    CONVERSATION = "conversation"

class EmbeddingModel(str, Enum):
    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    COHERE_EMBED_ENGLISH = "cohere-embed-english"
    COHERE_EMBED_MULTILINGUAL = "cohere-embed-multilingual"
    BGE_SMALL = "bge-small-en"
    BGE_LARGE = "bge-large-en"
    CUSTOM = "custom"

class ChunkingStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    CUSTOM = "custom"

class VectorStore(str, Enum):
    QDRANT = "qdrant"
    PINECONE = "pinecone"
    MILVUS = "milvus"
    REDIS = "redis"
    CHROMA = "chroma"
    POSTGRES = "postgres"
    SUPABASE = "supabase"
    CUSTOM = "custom"

class FineTuningMethod(str, Enum):
    FULL = "full_fine_tuning"
    LORA = "lora"
    QLORA = "qlora"
    PEFT = "peft"
    NONE = "none"

class RagConfig(BaseModel):
    enabled: bool = False
    embedding_model: Optional[EmbeddingModel] = None
    chunking_strategy: Optional[ChunkingStrategy] = None
    chunk_size: Optional[int] = 300
    chunk_overlap: Optional[int] = 50
    vector_store: Optional[VectorStore] = None
    vector_store_config: Optional[Dict[str, Any]] = {}
    knowledge_sources: List[str] = []
    hybrid_search: bool = False
    reranking_enabled: bool = False

class FineTuningConfig(BaseModel):
    enabled: bool = False
    method: FineTuningMethod = FineTuningMethod.NONE
    dataset_path: Optional[str] = None
    learning_rate: Optional[float] = 2e-5
    epochs: Optional[int] = 3
    batch_size: Optional[int] = 8
    model_adapter_path: Optional[str] = None
    training_status: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None

class AgentBase(BaseModel):
    name: str
    type: AgentType
    description: Optional[str] = None
    tools: List[str] = []
    model: Optional[AgentModel] = AgentModel.GPT_3_5_TURBO
    capabilities: List[AgentCapability] = []
    parent_id: Optional[str] = None
    child_ids: List[str] = []
    system_prompt: Optional[str] = None
    knowledge_base_ids: List[str] = []
    rag_config: Optional[RagConfig] = RagConfig()
    fine_tuning_config: Optional[FineTuningConfig] = FineTuningConfig()
    metadata: Dict[str, Any] = {}

class Agent(AgentBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    status: AgentStatus = AgentStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c88",
                "name": "CustomerServiceAgent",
                "type": "customer_service",
                "description": "Handles customer inquiries and service requests",
                "tools": ["customer_lookup", "service_request_create"],
                "model": "gpt-3.5-turbo",
                "capabilities": ["question_answering", "conversation"],
                "parent_id": None,
                "child_ids": [],
                "system_prompt": "You are a helpful customer service assistant...",
                "knowledge_base_ids": [],
                "rag_config": {
                    "enabled": False
                },
                "fine_tuning_config": {
                    "enabled": False,
                    "method": "none"
                },
                "metadata": {},
                "status": "active",
                "created_at": "2023-06-01T12:00:00",
                "updated_at": "2023-06-01T12:00:00",
                "last_active": "2023-06-01T12:05:00"
            }
        }
    )

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AgentType] = None
    description: Optional[str] = None
    tools: Optional[List[str]] = None
    model: Optional[AgentModel] = None
    capabilities: Optional[List[AgentCapability]] = None
    parent_id: Optional[str] = None
    child_ids: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    knowledge_base_ids: Optional[List[str]] = None
    rag_config: Optional[RagConfig] = None
    fine_tuning_config: Optional[FineTuningConfig] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[AgentStatus] = None

class AgentTemplate(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    description: str
    type: AgentType
    system_prompt: str
    tools: List[str] = []
    model: AgentModel = AgentModel.GPT_3_5_TURBO
    capabilities: List[AgentCapability] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={}
    )

# Add AgentTemplateCreate class
class AgentTemplateCreate(BaseModel):
    name: str
    description: str
    type: AgentType
    system_prompt: str
    tools: List[str] = []
    model: AgentModel = AgentModel.GPT_3_5_TURBO
    capabilities: List[AgentCapability] = []
    metadata: Dict[str, Any] = {}

# Add AgentTemplateUpdate class
class AgentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AgentType] = None
    system_prompt: Optional[str] = None
    tools: Optional[List[str]] = None
    model: Optional[AgentModel] = None
    capabilities: Optional[List[AgentCapability]] = None
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeSource(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    source_type: str  # file, database, api, etc.
    location: str  # file path, URL, etc.
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={}
    )

# Add KnowledgeSourceCreate class
class KnowledgeSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: str
    location: str
    metadata: Dict[str, Any] = {}

# Add KnowledgeSourceUpdate class
class KnowledgeSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Message Models for Agent Communication
class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class Message(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    conversation_id: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={}
    )

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    customer_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    status: ConversationStatus = ConversationStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={}
    )

# Settings Models
class ApiKeySetting(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    key_name: str
    key_value: str
    is_encrypted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c90",
                "key_name": "ANTHROPIC_API_KEY",
                "key_value": "sk-ant-api-...",
                "is_encrypted": False,
                "created_at": "2023-06-01T12:00:00",
                "updated_at": "2023-06-01T12:00:00"
            }
        }
    )

class ApiKeyCreate(BaseModel):
    key_name: str
    key_value: str

class SmartlistType(str, Enum):
    CUSTOMER = "customer"
    SERVICE_REQUEST = "service_request"
    TECHNICIAN = "technician"

class SmartlistBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: SmartlistType
    filter_criteria: Dict[str, Any] = {}
    is_public: bool = False
    owner_id: str

class Smartlist(SmartlistBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": "60d21b4967d0d8992e610c85",
                "name": "High priority refrigerator repairs",
                "description": "All refrigerator repairs with high or urgent priority",
                "type": "service_request",
                "filter_criteria": {
                    "appliance_type": "refrigerator",
                    "priority": ["high", "urgent"]
                },
                "is_public": True,
                "owner_id": "60d21b4967d0d8992e610c87",
                "created_at": "2023-06-01T12:00:00",
                "updated_at": "2023-06-01T12:00:00"
            }
        }
    )

class SmartlistCreate(SmartlistBase):
    pass

class SmartlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None 