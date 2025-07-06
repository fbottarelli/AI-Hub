import os
import uuid
import shutil
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import streamlit as st

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def format_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str

def format_date_only(date_str: str) -> str:
    """Format date string for display (date only)"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str

def ensure_upload_directory(directory: str = "health_data/uploads") -> str:
    """Ensure upload directory exists"""
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory

def save_uploaded_file(uploaded_file, upload_dir: str = "health_data/uploads") -> Optional[str]:
    """Save uploaded file and return the file path"""
    try:
        # Ensure upload directory exists
        ensure_upload_directory(upload_dir)
        
        # Generate unique filename
        file_extension = Path(uploaded_file.name).suffix
        unique_filename = f"{generate_id()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def get_file_type(filename: str) -> str:
    """Determine file type based on extension"""
    extension = Path(filename).suffix.lower()
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
    
    if extension in image_extensions:
        return 'image'
    elif extension in document_extensions:
        return 'document'
    else:
        return 'other'

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def parse_tags(tags_input: str) -> list:
    """Parse tags from comma-separated string"""
    if not tags_input:
        return []
    return [tag.strip() for tag in tags_input.split(',') if tag.strip()]

def tags_to_string(tags: list) -> str:
    """Convert tags list to comma-separated string"""
    return ', '.join(tags) if tags else ''

def get_category_color(category: str) -> str:
    """Get color for category badge"""
    colors = {
        'medication': '#FF6B6B',      # Red - medications
        'treatment': '#4ECDC4',       # Teal - treatments
        'diagnosis': '#45B7D1',       # Blue - diagnoses
        'daily_note': '#96CEB4',      # Green - daily notes
        'appointment': '#FFEAA7',     # Yellow - appointments
        'symptoms': '#FF9F43',        # Orange - symptoms
        'analysis': '#6C5CE7',        # Purple - analysis/tests
        'condition': '#E17055'        # Coral - conditions
    }
    return colors.get(category, '#DDA0DD')

def get_condition_status_color(status: str) -> str:
    """Get color for condition status"""
    colors = {
        'active': '#FF6B6B',          # Red - active
        'resolved': '#00B894',        # Green - resolved
        'chronic': '#FDCB6E',         # Yellow - chronic
        'monitoring': '#74B9FF'       # Blue - monitoring
    }
    return colors.get(status, '#DDA0DD')

def get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        'mild': '#00B894',            # Green - mild
        'moderate': '#FDCB6E',        # Yellow - moderate
        'severe': '#FF7675'           # Red - severe
    }
    return colors.get(severity, '#DDA0DD')

def display_category_badge(category: str):
    """Display category as a colored badge"""
    color = get_category_color(category)
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.8em; font-weight: bold;">{category.upper()}</span>',
        unsafe_allow_html=True
    )

def display_condition_status_badge(status: str):
    """Display condition status as a colored badge"""
    color = get_condition_status_color(status)
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.8em; font-weight: bold;">{status.upper()}</span>',
        unsafe_allow_html=True
    )

def display_severity_badge(severity: str):
    """Display severity as a colored badge"""
    color = get_severity_color(severity)
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.8em; font-weight: bold;">{severity.upper()}</span>',
        unsafe_allow_html=True
    )

def display_linked_badge():
    """Display a badge indicating record is linked to a condition"""
    st.markdown(
        f'<span style="background-color: #00B894; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.7em; font-weight: bold;">🔗 LINKED</span>',
        unsafe_allow_html=True
    )

def display_unlinked_badge():
    """Display a badge indicating record is not linked to any condition"""
    st.markdown(
        f'<span style="background-color: #FDCB6E; color: white; padding: 2px 8px; '
        f'border-radius: 12px; font-size: 0.7em; font-weight: bold;">⚠️ UNLINKED</span>',
        unsafe_allow_html=True
    )

def get_record_type_info(category: str) -> dict:
    """Get information about record type including icon and description"""
    info = {
        'medication': {
            'icon': '💊',
            'name': 'Medication',
            'description': 'Medications, prescriptions, and drug treatments'
        },
        'treatment': {
            'icon': '🏥',
            'name': 'Treatment',
            'description': 'Medical treatments, procedures, and therapies'
        },
        'diagnosis': {
            'icon': '🩺',
            'name': 'Diagnosis',
            'description': 'Medical diagnoses and conditions'
        },
        'daily_note': {
            'icon': '📝',
            'name': 'Daily Note',
            'description': 'Daily health observations and notes'
        },
        'appointment': {
            'icon': '👩‍⚕️',
            'name': 'Appointment',
            'description': 'Medical appointments and consultations'
        },
        'symptoms': {
            'icon': '🤒',
            'name': 'Symptoms',
            'description': 'Physical symptoms and health concerns'
        },
        'analysis': {
            'icon': '🔬',
            'name': 'Analysis',
            'description': 'Medical tests, lab results, and health measurements'
        }
    }
    return info.get(category, {
        'icon': '📋',
        'name': category.title(),
        'description': f'{category.title()} records'
    })

def format_condition_name(condition_name: str) -> str:
    """Format condition name for display"""
    if not condition_name:
        return "Unknown Condition"
    return condition_name.title()

def get_condition_categories() -> List[str]:
    """Get list of common condition categories"""
    return [
        "Cardiovascular",
        "Respiratory",
        "Gastrointestinal",
        "Musculoskeletal",
        "Neurological",
        "Endocrine",
        "Dermatological",
        "Mental Health",
        "Infectious Disease",
        "Autoimmune",
        "Other"
    ]

def validate_email(email: str) -> bool:
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_record_summary(record) -> str:
    """Get a summary of a health record for display"""
    summary = f"{record.title}"
    if record.condition_id:
        summary += " (Linked)"
    else:
        summary += " (Unlinked)"
    return summary 