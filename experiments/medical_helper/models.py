from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import json
import os

@dataclass
class Condition:
    """Model for a health condition/diagnosis"""
    id: str
    name: str  # e.g., "Hypertension", "Type 2 Diabetes"
    description: str
    diagnosed_date: Optional[str]  # ISO format string
    status: str  # active, resolved, chronic, monitoring
    severity: str  # mild, moderate, severe
    tags: List[str]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class HealthRecord:
    """Model for a health record entry"""
    id: str
    category: str  # medication, treatment, diagnosis, daily_note, appointment, symptoms, analysis
    title: str
    description: str
    date: str  # ISO format string
    tags: List[str]
    metadata: Dict[str, Any]  # Additional flexible data
    attachments: List[str]  # List of file paths
    created_at: str
    updated_at: str
    # New relationship fields
    condition_id: Optional[str] = None  # Link to a condition
    related_records: List[str] = None  # List of related record IDs
    
    def __post_init__(self):
        if self.related_records is None:
            self.related_records = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthRecord':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class FileAttachment:
    """Model for file attachments"""
    id: str
    filename: str
    original_name: str
    file_path: str
    file_type: str  # image, document, etc.
    size: int
    uploaded_at: str
    description: str
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileAttachment':
        """Create from dictionary"""
        return cls(**data)

class HealthRecordManager:
    """Manager for health records, conditions, and file attachments"""
    
    def __init__(self, data_dir: str = "health_data"):
        self.data_dir = data_dir
        self.records: List[HealthRecord] = []
        self.conditions: List[Condition] = []
        self.attachments: List[FileAttachment] = []
        self.ensure_data_directory()
        self.load_data()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "uploads"), exist_ok=True)
    
    def load_data(self):
        """Load data from JSON files"""
        try:
            # Load records
            records_file = os.path.join(self.data_dir, "records.json")
            if os.path.exists(records_file):
                with open(records_file, 'r') as f:
                    data = json.load(f)
                    self.records = [HealthRecord.from_dict(record) for record in data.get('records', [])]
            
            # Load conditions
            conditions_file = os.path.join(self.data_dir, "conditions.json")
            if os.path.exists(conditions_file):
                with open(conditions_file, 'r') as f:
                    data = json.load(f)
                    self.conditions = [Condition.from_dict(condition) for condition in data.get('conditions', [])]
            
            # Load attachments
            attachments_file = os.path.join(self.data_dir, "attachments.json")
            if os.path.exists(attachments_file):
                with open(attachments_file, 'r') as f:
                    data = json.load(f)
                    self.attachments = [FileAttachment.from_dict(att) for att in data.get('attachments', [])]
        except Exception as e:
            print(f"Error loading data: {e}")
            self.records = []
            self.conditions = []
            self.attachments = []
    
    def save_data(self):
        """Save data to JSON files"""
        try:
            # Save records
            records_file = os.path.join(self.data_dir, "records.json")
            with open(records_file, 'w') as f:
                json.dump({'records': [record.to_dict() for record in self.records]}, f, indent=2)
            
            # Save conditions
            conditions_file = os.path.join(self.data_dir, "conditions.json")
            with open(conditions_file, 'w') as f:
                json.dump({'conditions': [condition.to_dict() for condition in self.conditions]}, f, indent=2)
            
            # Save attachments
            attachments_file = os.path.join(self.data_dir, "attachments.json")
            with open(attachments_file, 'w') as f:
                json.dump({'attachments': [att.to_dict() for att in self.attachments]}, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # Health Record methods
    def add_record(self, record: HealthRecord) -> str:
        """Add a new health record"""
        self.records.append(record)
        self.save_data()
        return record.id
    
    def update_record(self, record_id: str, updated_record: HealthRecord) -> bool:
        """Update an existing health record"""
        for i, record in enumerate(self.records):
            if record.id == record_id:
                self.records[i] = updated_record
                self.save_data()
                return True
        return False
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a health record"""
        for i, record in enumerate(self.records):
            if record.id == record_id:
                del self.records[i]
                self.save_data()
                return True
        return False
    
    def get_record(self, record_id: str) -> Optional[HealthRecord]:
        """Get a specific health record"""
        for record in self.records:
            if record.id == record_id:
                return record
        return None
    
    def get_all_records(self) -> List[HealthRecord]:
        """Get all health records"""
        return self.records.copy()
    
    def get_records_by_condition(self, condition_id: str) -> List[HealthRecord]:
        """Get all records linked to a specific condition"""
        return [r for r in self.records if r.condition_id == condition_id]
    
    def get_unlinked_records(self, category: str = None) -> List[HealthRecord]:
        """Get records not linked to any condition"""
        unlinked = [r for r in self.records if not r.condition_id]
        if category:
            unlinked = [r for r in unlinked if r.category == category]
        return unlinked
    
    def search_records(self, query: str = "", category: str = "", tags: List[str] = None, condition_id: str = None) -> List[HealthRecord]:
        """Search health records"""
        results = self.records.copy()
        
        if query:
            query_lower = query.lower()
            results = [r for r in results if 
                      query_lower in r.title.lower() or 
                      query_lower in r.description.lower()]
        
        if category:
            results = [r for r in results if r.category == category]
        
        if tags:
            results = [r for r in results if any(tag in r.tags for tag in tags)]
        
        if condition_id:
            results = [r for r in results if r.condition_id == condition_id]
        
        return results
    
    # Condition methods
    def add_condition(self, condition: Condition) -> str:
        """Add a new condition"""
        self.conditions.append(condition)
        self.save_data()
        return condition.id
    
    def update_condition(self, condition_id: str, updated_condition: Condition) -> bool:
        """Update an existing condition"""
        for i, condition in enumerate(self.conditions):
            if condition.id == condition_id:
                self.conditions[i] = updated_condition
                self.save_data()
                return True
        return False
    
    def delete_condition(self, condition_id: str) -> bool:
        """Delete a condition and unlink all related records"""
        # First, unlink all records from this condition
        for record in self.records:
            if record.condition_id == condition_id:
                record.condition_id = None
        
        # Then delete the condition
        for i, condition in enumerate(self.conditions):
            if condition.id == condition_id:
                del self.conditions[i]
                self.save_data()
                return True
        return False
    
    def get_condition(self, condition_id: str) -> Optional[Condition]:
        """Get a specific condition"""
        for condition in self.conditions:
            if condition.id == condition_id:
                return condition
        return None
    
    def get_all_conditions(self) -> List[Condition]:
        """Get all conditions"""
        return self.conditions.copy()
    
    def link_record_to_condition(self, record_id: str, condition_id: str) -> bool:
        """Link a record to a condition"""
        record = self.get_record(record_id)
        condition = self.get_condition(condition_id)
        
        if record and condition:
            record.condition_id = condition_id
            self.save_data()
            return True
        return False
    
    def unlink_record_from_condition(self, record_id: str) -> bool:
        """Unlink a record from its condition"""
        record = self.get_record(record_id)
        if record:
            record.condition_id = None
            self.save_data()
            return True
        return False
    
    # File attachment methods
    def add_attachment(self, attachment: FileAttachment) -> str:
        """Add a file attachment"""
        self.attachments.append(attachment)
        self.save_data()
        return attachment.id
    
    def get_attachment(self, attachment_id: str) -> Optional[FileAttachment]:
        """Get a specific file attachment"""
        for attachment in self.attachments:
            if attachment.id == attachment_id:
                return attachment
        return None 