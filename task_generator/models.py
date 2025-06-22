from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    """Supported task types."""
    HTTP_REQUEST = "http_request"
    MATH_CALCULATION = "math_calculation"
    FILE_OPERATION = "file_operation"
    DATA_TRANSFORMATION = "data_transformation"

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class TaskStatus(str, Enum):
    """Task status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"

class TaskRequest(BaseModel):
    """Model for task submission to processor."""
    task_type: TaskType
    payload: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timeout: Optional[int] = Field(default=300, ge=1, le=3600)
    retry_count: Optional[int] = Field(default=3, ge=0, le=10)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TaskResponse(BaseModel):
    """Model for task submission response."""
    task_id: str
    job_id: Optional[str] = None
    status: TaskStatus
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BatchTaskRequest(BaseModel):
    """Model for batch task submission."""
    tasks: List[TaskRequest] = Field(..., min_items=1, max_items=50)
    batch_id: Optional[str] = None

class BatchTaskResponse(BaseModel):
    """Model for batch task submission response."""
    batch_id: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    results: List[TaskResponse]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TaskTemplate(BaseModel):
    """Model for task templates."""
    template_id: str
    name: str
    description: str
    task_type: TaskType
    payload_template: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timeout: Optional[int] = 300
    retry_count: Optional[int] = 3
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskGenerationConfig(BaseModel):
    """Model for task generation configuration."""
    enabled: bool = True
    interval_seconds: int = Field(default=5, ge=1, le=3600)
    max_concurrent: int = Field(default=10, ge=1, le=100)
    task_type_weights: Dict[TaskType, float] = Field(default_factory=dict)
    priority_weights: Dict[Priority, float] = Field(default_factory=dict)

class TaskStats(BaseModel):
    """Model for task statistics."""
    total_generated: int
    total_sent: int
    total_failed: int
    total_retried: int
    by_task_type: Dict[TaskType, int]
    by_priority: Dict[Priority, int]
    by_status: Dict[TaskStatus, int]
    success_rate: float
    average_response_time: float
    last_24_hours: Dict[str, int]

class HealthCheck(BaseModel):
    """Model for health check response."""
    service: str
    status: str
    version: str
    timestamp: datetime
    uptime: float
    task_processor_connected: bool
    database_connected: bool
    redis_connected: bool

class MetricsData(BaseModel):
    """Model for metrics data."""
    tasks_generated_per_minute: float
    tasks_sent_per_minute: float
    success_rate: float
    average_response_time: float
    active_connections: int
    memory_usage: float
    cpu_usage: float

# HTTP Request specific models
class HttpRequestPayload(BaseModel):
    """Model for HTTP request task payload."""
    url: HttpUrl
    method: str = Field(default="GET", regex="^(GET|POST|PUT|DELETE|PATCH)$")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    data: Optional[Union[Dict[str, Any], str]] = None
    timeout: Optional[int] = Field(default=30, ge=1, le=300)
    verify_ssl: bool = True

# Math Calculation specific models
class MathOperation(str, Enum):
    """Supported math operations."""
    ADD = "add"
    MULTIPLY = "multiply"
    FACTORIAL = "factorial"
    FIBONACCI = "fibonacci"
    PRIME_CHECK = "prime_check"
    SQUARE_ROOT = "square_root"
    POWER = "power"

class MathCalculationPayload(BaseModel):
    """Model for math calculation task payload."""
    operation: MathOperation
    numbers: Optional[List[Union[int, float]]] = None
    number: Optional[Union[int, float]] = None
    n: Optional[int] = None
    base: Optional[Union[int, float]] = None
    exponent: Optional[int] = None

# File Operation specific models
class FileOperation(str, Enum):
    """Supported file operations."""
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"

class FileOperationPayload(BaseModel):
    """Model for file operation task payload."""
    operation: FileOperation
    filename: str
    content: Optional[str] = None
    source_path: Optional[str] = None
    destination_path: Optional[str] = None
    encoding: str = "utf-8"

# Data Transformation specific models
class DataTransformationType(str, Enum):
    """Supported data transformation types."""
    JSON_TO_CSV = "json_to_csv"
    CSV_TO_JSON = "csv_to_json"
    XML_TO_JSON = "xml_to_json"
    DATA_FILTER = "data_filter"
    DATA_SORT = "data_sort"
    DATA_AGGREGATE = "data_aggregate"

class DataTransformationPayload(BaseModel):
    """Model for data transformation task payload."""
    transformation_type: DataTransformationType
    data: Union[Dict[str, Any], str, List[Any]]
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    output_format: Optional[str] = None 