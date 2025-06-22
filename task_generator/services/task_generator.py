import random
import math
import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from ..models import (
    TaskRequest, TaskType, Priority, HttpRequestPayload, 
    MathCalculationPayload, FileOperationPayload, DataTransformationPayload,
    MathOperation, FileOperation, DataTransformationType
)
from ..config import settings

class TaskGeneratorService:
    """Service for generating various types of tasks optimized for 1-2 minute execution."""
    
    def __init__(self):
        self.http_endpoints = settings.HTTP_ENDPOINTS
        self.task_type_weights = settings.TASK_TYPE_WEIGHTS
        self.priority_weights = settings.PRIORITY_WEIGHTS
        
        # Heavy endpoints that take time to respond
        self.heavy_http_endpoints = [
            "https://httpbin.org/delay/30",  # 30 second delay
            "https://httpbin.org/delay/45",  # 45 second delay
            "https://httpbin.org/delay/60",  # 60 second delay
            "https://jsonplaceholder.typicode.com/posts",  # Large response
            "https://api.github.com/repos/torvalds/linux/commits",  # Large response
            "https://api.publicapis.org/entries",  # Large response
        ]
        
        # Sample data for transformations
        self.sample_json_data = [
            {"name": "John Doe", "age": 30, "city": "New York", "salary": 75000},
            {"name": "Jane Smith", "age": 25, "city": "Los Angeles", "salary": 65000},
            {"name": "Bob Johnson", "age": 35, "city": "Chicago", "salary": 80000},
            {"name": "Alice Brown", "age": 28, "city": "Houston", "salary": 70000}
        ]
        
        self.sample_csv_data = """name,age,city,salary
John Doe,30,New York,75000
Jane Smith,25,Los Angeles,65000
Bob Johnson,35,Chicago,80000
Alice Brown,28,Houston,70000"""
        
        self.sample_xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<employees>
    <employee>
        <name>John Doe</name>
        <age>30</age>
        <city>New York</city>
        <salary>75000</salary>
    </employee>
    <employee>
        <name>Jane Smith</name>
        <age>25</age>
        <city>Los Angeles</city>
        <salary>65000</salary>
    </employee>
</employees>"""
    
    def generate_random_task(self) -> TaskRequest:
        """Generate a random task with weighted distribution optimized for 1-2 minute execution."""
        # Select task type based on weights
        task_type = self._select_weighted_choice(list(self.task_type_weights.keys()), 
                                               list(self.task_type_weights.values()))
        
        # Select priority based on weights
        priority = self._select_weighted_choice(list(self.priority_weights.keys()),
                                              list(self.priority_weights.values()))
        
        # Generate payload based on task type
        if task_type == TaskType.HTTP_REQUEST:
            payload = self._generate_heavy_http_payload()
        elif task_type == TaskType.MATH_CALCULATION:
            payload = self._generate_heavy_math_payload()
        elif task_type == TaskType.FILE_OPERATION:
            payload = self._generate_heavy_file_payload()
        elif task_type == TaskType.DATA_TRANSFORMATION:
            payload = self._generate_heavy_data_transformation_payload()
        else:
            payload = {"message": "Unknown task type"}
        
        return TaskRequest(
            task_type=TaskType(task_type),
            payload=payload,
            priority=Priority(priority),
            timeout=random.randint(90, 180),  # 1.5-3 minutes timeout
            retry_count=random.randint(1, 3),
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "generator_id": str(uuid.uuid4())[:8],
                "estimated_duration": "1-2 minutes"
            }
        )
    
    def _select_weighted_choice(self, choices: List, weights: List[float]) -> str:
        """Select a choice based on weights."""
        return random.choices(choices, weights=weights, k=1)[0]
    
    def _generate_heavy_http_payload(self) -> Dict[str, Any]:
        """Generate HTTP request payload that takes 1-2 minutes to execute."""
        # Mix of heavy endpoints and regular ones
        if random.random() < 0.7:  # 70% chance for heavy endpoint
            endpoint = random.choice(self.heavy_http_endpoints)
        else:
            endpoint = random.choice(self.http_endpoints)
        
        method = random.choice(["GET", "POST"])
        
        payload = {
            "url": endpoint,
            "method": method,
            "headers": {
                "User-Agent": "TaskGenerator/1.0",
                "Accept": "application/json",
                "X-Request-ID": str(uuid.uuid4()),
                "X-Heavy-Task": "true"
            },
            "timeout": random.randint(60, 120),  # 1-2 minutes timeout
            "verify_ssl": True
        }
        
        if method == "POST":
            # Generate large payload for POST requests
            large_data = {
                "message": f"Generated heavy request at {datetime.utcnow().isoformat()}",
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().timestamp(),
                "large_payload": {
                    "items": [{"id": i, "data": f"item_{i}" * 100} for i in range(1000)],
                    "metadata": {"size": "large", "processing_time": "1-2 minutes"}
                }
            }
            payload["data"] = large_data
        
        return payload
    
    def _generate_heavy_math_payload(self) -> Dict[str, Any]:
        """Generate math calculation payload that takes 1-2 minutes to execute."""
        operations = [
            {
                "operation": MathOperation.FACTORIAL,
                "number": random.randint(100000, 500000)  # Very large factorial
            },
            {
                "operation": MathOperation.FIBONACCI,
                "n": random.randint(100000, 500000)  # Very large fibonacci
            },
            {
                "operation": MathOperation.PRIME_CHECK,
                "number": random.randint(1000000, 10000000)  # Large prime check
            },
            {
                "operation": MathOperation.POWER,
                "base": random.randint(2, 10),
                "exponent": random.randint(1000, 5000)  # Large power calculation
            },
            {
                "operation": "matrix_multiply",  # Custom heavy operation
                "matrix_size": random.randint(100, 500),
                "iterations": random.randint(10, 50)
            },
            {
                "operation": "prime_generation",  # Generate large primes
                "bit_length": random.randint(512, 1024),
                "count": random.randint(5, 20)
            },
            {
                "operation": "pi_calculation",  # Calculate pi to many digits
                "digits": random.randint(10000, 50000)
            }
        ]
        
        return random.choice(operations)
    
    def _generate_heavy_file_payload(self) -> Dict[str, Any]:
        """Generate file operation payload that takes 1-2 minutes to execute."""
        operations = [
            {
                "operation": FileOperation.WRITE,
                "filename": f"large_file_{uuid.uuid4().hex[:8]}.txt",
                "content": self._generate_large_content(),
                "size_mb": random.randint(10, 50)
            },
            {
                "operation": FileOperation.APPEND,
                "filename": "large_log.txt",
                "content": self._generate_large_log_content(),
                "entries": random.randint(1000, 5000)
            },
            {
                "operation": FileOperation.READ,
                "filename": "large_sample.txt",
                "content": "Large file content for reading",
                "read_size_mb": random.randint(20, 100)
            },
            {
                "operation": "file_compression",
                "filename": f"compress_{uuid.uuid4().hex[:8]}.txt",
                "content": self._generate_large_content(),
                "algorithm": random.choice(["gzip", "bzip2", "lzma"])
            },
            {
                "operation": "file_encryption",
                "filename": f"encrypt_{uuid.uuid4().hex[:8]}.txt",
                "content": self._generate_large_content(),
                "algorithm": random.choice(["AES", "RSA", "ChaCha20"])
            },
            {
                "operation": "file_search",
                "filename": "large_search_file.txt",
                "content": self._generate_searchable_content(),
                "search_pattern": "complex_pattern",
                "recursive": True
            }
        ]
        
        return random.choice(operations)
    
    def _generate_heavy_data_transformation_payload(self) -> Dict[str, Any]:
        """Generate data transformation payload that takes 1-2 minutes to execute."""
        transformations = [
            {
                "transformation_type": DataTransformationType.JSON_TO_CSV,
                "data": self._generate_large_json_data(),
                "options": {"include_headers": True, "chunk_size": 1000}
            },
            {
                "transformation_type": DataTransformationType.CSV_TO_JSON,
                "data": self._generate_large_csv_data(),
                "options": {"delimiter": ",", "chunk_size": 1000}
            },
            {
                "transformation_type": DataTransformationType.XML_TO_JSON,
                "data": self._generate_large_xml_data(),
                "options": {"pretty_print": True, "chunk_size": 1000}
            },
            {
                "transformation_type": DataTransformationType.DATA_FILTER,
                "data": self._generate_large_json_data(),
                "options": {
                    "filter_key": "value", 
                    "filter_value": 100, 
                    "operator": ">=",
                    "parallel": True
                }
            },
            {
                "transformation_type": DataTransformationType.DATA_SORT,
                "data": self._generate_large_json_data(),
                "options": {
                    "sort_key": "timestamp", 
                    "reverse": True,
                    "parallel": True,
                    "chunk_size": 1000
                }
            },
            {
                "transformation_type": DataTransformationType.DATA_AGGREGATE,
                "data": self._generate_large_json_data(),
                "options": {
                    "group_by": "category", 
                    "aggregate": "value", 
                    "operation": "average",
                    "parallel": True
                }
            },
            {
                "transformation_type": "data_machine_learning",
                "data": self._generate_ml_dataset(),
                "options": {
                    "algorithm": random.choice(["kmeans", "dbscan", "hierarchical"]),
                    "clusters": random.randint(5, 20),
                    "iterations": random.randint(100, 500)
                }
            }
        ]
        
        return random.choice(transformations)
    
    def _generate_large_content(self) -> str:
        """Generate large content for file operations."""
        lines = []
        for i in range(random.randint(10000, 50000)):
            lines.append(f"Line {i}: {uuid.uuid4()} - {datetime.utcnow().isoformat()} - " + 
                        "X" * random.randint(50, 200))
        return "\n".join(lines)
    
    def _generate_large_log_content(self) -> str:
        """Generate large log content."""
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        messages = [
            "Processing request", "Database query executed", "File operation completed",
            "Network request sent", "Cache updated", "User authentication",
            "Data validation", "API call made", "Background job started"
        ]
        
        lines = []
        for i in range(random.randint(1000, 5000)):
            timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 86400))
            level = random.choice(log_levels)
            message = random.choice(messages)
            lines.append(f"[{timestamp.isoformat()}] {level}: {message} - ID: {uuid.uuid4()}")
        
        return "\n".join(lines)
    
    def _generate_searchable_content(self) -> str:
        """Generate content with searchable patterns."""
        patterns = ["ERROR", "WARNING", "SUCCESS", "FAILED", "COMPLETED"]
        lines = []
        for i in range(random.randint(5000, 20000)):
            if random.random() < 0.1:  # 10% chance for pattern
                pattern = random.choice(patterns)
                lines.append(f"Line {i}: Found {pattern} pattern at {datetime.utcnow().isoformat()}")
            else:
                lines.append(f"Line {i}: Regular content {uuid.uuid4()}")
        return "\n".join(lines)
    
    def _generate_large_json_data(self) -> List[Dict[str, Any]]:
        """Generate large JSON dataset."""
        data = []
        for i in range(random.randint(10000, 50000)):
            data.append({
                "id": i,
                "name": f"Item_{i}",
                "value": random.randint(1, 1000),
                "category": random.choice(["A", "B", "C", "D", "E"]),
                "timestamp": (datetime.utcnow() - timedelta(seconds=random.randint(0, 86400))).isoformat(),
                "metadata": {
                    "tags": [f"tag_{j}" for j in range(random.randint(1, 5))],
                    "score": random.uniform(0, 100),
                    "active": random.choice([True, False])
                }
            })
        return data
    
    def _generate_large_csv_data(self) -> str:
        """Generate large CSV dataset."""
        lines = ["id,name,value,category,timestamp,tags,score,active"]
        for i in range(random.randint(10000, 50000)):
            lines.append(f"{i},Item_{i},{random.randint(1, 1000)},{random.choice(['A', 'B', 'C', 'D', 'E'])},"
                        f"{datetime.utcnow().isoformat()},tag1;tag2;tag3,{random.uniform(0, 100)},{random.choice(['true', 'false'])}")
        return "\n".join(lines)
    
    def _generate_large_xml_data(self) -> str:
        """Generate large XML dataset."""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<dataset>']
        for i in range(random.randint(10000, 50000)):
            xml_lines.append(f'''  <item id="{i}">
    <name>Item_{i}</name>
    <value>{random.randint(1, 1000)}</value>
    <category>{random.choice(['A', 'B', 'C', 'D', 'E'])}</category>
    <timestamp>{datetime.utcnow().isoformat()}</timestamp>
    <metadata>
      <tags>tag1,tag2,tag3</tags>
      <score>{random.uniform(0, 100)}</score>
      <active>{random.choice(['true', 'false'])}</active>
    </metadata>
  </item>''')
        xml_lines.append('</dataset>')
        return "\n".join(xml_lines)
    
    def _generate_ml_dataset(self) -> List[Dict[str, Any]]:
        """Generate machine learning dataset."""
        data = []
        for i in range(random.randint(5000, 20000)):
            data.append({
                "features": [random.uniform(0, 1) for _ in range(10)],
                "label": random.choice([0, 1]),
                "cluster": random.randint(0, 9)
            })
        return data
    
    def generate_batch_tasks(self, count: int) -> List[TaskRequest]:
        """Generate a batch of tasks."""
        return [self.generate_random_task() for _ in range(count)]
    
    def generate_task_by_type(self, task_type: TaskType, **kwargs) -> TaskRequest:
        """Generate a specific type of task."""
        priority = kwargs.get('priority', Priority.NORMAL)
        timeout = kwargs.get('timeout', 120)  # Default 2 minutes
        retry_count = kwargs.get('retry_count', 3)
        
        if task_type == TaskType.HTTP_REQUEST:
            payload = self._generate_heavy_http_payload()
        elif task_type == TaskType.MATH_CALCULATION:
            payload = self._generate_heavy_math_payload()
        elif task_type == TaskType.FILE_OPERATION:
            payload = self._generate_heavy_file_payload()
        elif task_type == TaskType.DATA_TRANSFORMATION:
            payload = self._generate_heavy_data_transformation_payload()
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
        
        return TaskRequest(
            task_type=task_type,
            payload=payload,
            priority=priority,
            timeout=timeout,
            retry_count=retry_count,
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "generator_id": str(uuid.uuid4())[:8],
                "custom": kwargs.get('metadata', {}),
                "estimated_duration": "1-2 minutes"
            }
        )
    
    def generate_stress_test_tasks(self, count: int) -> List[TaskRequest]:
        """Generate tasks for stress testing."""
        tasks = []
        for i in range(count):
            # Mix of different priorities and types
            priority = random.choice([Priority.HIGH, Priority.NORMAL, Priority.LOW])
            task_type = random.choice(list(TaskType))
            
            task = self.generate_task_by_type(
                task_type=task_type,
                priority=priority,
                timeout=random.randint(60, 120),  # 1-2 minutes for stress test
                retry_count=random.randint(1, 3)
            )
            
            # Add stress test metadata
            task.metadata.update({
                "stress_test": True,
                "test_id": f"stress_{i}",
                "batch_size": count
            })
            
            tasks.append(task)
        
        return tasks
    
    def generate_scheduled_tasks(self, schedule_config: Dict[str, Any]) -> List[TaskRequest]:
        """Generate tasks based on schedule configuration."""
        tasks = []
        task_type = schedule_config.get('task_type', TaskType.HTTP_REQUEST)
        interval = schedule_config.get('interval_seconds', 60)
        count = schedule_config.get('count', 1)
        
        for i in range(count):
            task = self.generate_task_by_type(
                task_type=task_type,
                priority=schedule_config.get('priority', Priority.NORMAL),
                timeout=schedule_config.get('timeout', 120),
                retry_count=schedule_config.get('retry_count', 3)
            )
            
            # Add scheduling metadata
            task.metadata.update({
                "scheduled": True,
                "schedule_id": schedule_config.get('schedule_id', str(uuid.uuid4())),
                "interval_seconds": interval,
                "scheduled_at": datetime.utcnow().isoformat()
            })
            
            tasks.append(task)
        
        return tasks 