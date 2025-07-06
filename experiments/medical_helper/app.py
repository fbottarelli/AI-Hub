import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from pathlib import Path

# Import our custom modules
from models import HealthRecord, FileAttachment, HealthRecordManager, Condition
from utils import (
    generate_id, get_current_timestamp, format_date, format_date_only, save_uploaded_file,
    get_file_size, get_file_type, format_file_size, parse_tags, tags_to_string,
    display_category_badge, display_condition_status_badge, display_severity_badge,
    display_linked_badge, display_unlinked_badge, get_record_type_info,
    format_condition_name, get_condition_categories, truncate_text, ensure_upload_directory
)

# Page configuration
st.set_page_config(
    page_title="Medical Helper - Personal Health Tracker",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'health_manager' not in st.session_state:
    st.session_state.health_manager = HealthRecordManager()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

if 'editing_record' not in st.session_state:
    st.session_state.editing_record = None

if 'editing_condition' not in st.session_state:
    st.session_state.editing_condition = None

# Main app
def main():
    st.title("🏥 Medical Helper - Personal Health Tracker")
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        
        # Handle forced page changes
        if 'force_page' in st.session_state:
            st.session_state.current_page = st.session_state.force_page
            del st.session_state.force_page
        
        pages = ["Dashboard", "My Conditions", "Add New Record", "View All Records", "Search Records", "Unlinked Records"]
        
        # Get current page index
        try:
            default_index = pages.index(st.session_state.current_page)
        except ValueError:
            default_index = 0
            st.session_state.current_page = "Dashboard"
            
        page = st.radio(
            "Choose a page:",
            pages,
            index=default_index
        )
        
        # Update current page if user changed it via radio button
        if page != st.session_state.current_page:
            st.session_state.current_page = page
        
        # Show some statistics
        st.markdown("### 📊 Quick Stats")
        manager = st.session_state.health_manager
        total_records = len(manager.get_all_records())
        total_conditions = len(manager.get_all_conditions())
        unlinked_records = len(manager.get_unlinked_records())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Records", total_records)
            st.metric("Conditions", total_conditions)
        with col2:
            st.metric("Linked", total_records - unlinked_records)
            st.metric("Unlinked", unlinked_records)
        
        if total_records > 0:
            # Count by category
            categories = {}
            for record in manager.get_all_records():
                categories[record.category] = categories.get(record.category, 0) + 1
            
            st.markdown("**By Category:**")
            for category, count in categories.items():
                info = get_record_type_info(category)
                st.write(f"{info['icon']} {category.title()}: {count}")
        else:
            st.info("No records yet. Add your first health record!")
    
    # Main content area - use session state current_page for navigation
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        show_dashboard()
    elif current_page == "My Conditions":
        show_conditions_page()
    elif current_page == "Add New Record":
        show_add_record_form()
    elif current_page == "View All Records":
        show_all_records()
    elif current_page == "Search Records":
        show_search_records()
    elif current_page == "Unlinked Records":
        show_unlinked_records()

def show_dashboard():
    st.header("📊 Dashboard")
    
    manager = st.session_state.health_manager
    records = manager.get_all_records()
    conditions = manager.get_all_conditions()
    
    if not records and not conditions:
        st.info("Welcome to your Personal Health Tracker!")
        st.markdown("### 🚀 Get Started")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Your First Condition", use_container_width=True):
                st.session_state.current_page = "My Conditions"
                st.rerun()
            st.markdown("*Start by adding a health condition you're managing*")
        
        with col2:
            if st.button("Add Your First Record", use_container_width=True):
                st.session_state.current_page = "Add New Record"
                st.rerun()
            st.markdown("*Or jump right in with a health record*")
        
        return
    
    # Active conditions overview
    if conditions:
        st.subheader("🏥 Active Conditions")
        
        active_conditions = [c for c in conditions if c.status == 'active']
        if active_conditions:
            for condition in active_conditions:
                with st.expander(f"{condition.name} - {condition.status.title()}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        display_condition_status_badge(condition.status)
                        display_severity_badge(condition.severity)
                        st.write(f"**Description:** {condition.description}")
                        if condition.diagnosed_date:
                            st.write(f"**Diagnosed:** {format_date_only(condition.diagnosed_date)}")
                        if condition.tags:
                            st.write(f"**Tags:** {tags_to_string(condition.tags)}")
                        
                        # Show related records
                        related_records = manager.get_records_by_condition(condition.id)
                        if related_records:
                            st.write(f"**Related Records:** {len(related_records)}")
                            for record in related_records[:3]:  # Show first 3
                                info = get_record_type_info(record.category)
                                st.write(f"• {info['icon']} {record.title}")
                            if len(related_records) > 3:
                                st.write(f"... and {len(related_records) - 3} more")
                    
                    with col2:
                        if st.button(f"View Details", key=f"view_condition_{condition.id}"):
                            st.session_state.editing_condition = condition.id
                            st.session_state.current_page = "My Conditions"
                            st.rerun()
        else:
            st.info("No active conditions. All conditions are resolved or being monitored.")
    
    # Recent records
    if records:
        st.subheader("📝 Recent Records")
        
        # Sort by created date (most recent first)
        recent_records = sorted(records, key=lambda x: x.created_at, reverse=True)[:5]
        
        for record in recent_records:
            with st.expander(f"{record.title} - {format_date(record.created_at)}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    display_category_badge(record.category)
                    if record.condition_id:
                        display_linked_badge()
                        condition = manager.get_condition(record.condition_id)
                        if condition:
                            st.write(f"**Linked to:** {condition.name}")
                    else:
                        display_unlinked_badge()
                    
                    st.write(f"**Date:** {format_date(record.date)}")
                    st.write(f"**Description:** {truncate_text(record.description, 150)}")
                    if record.tags:
                        st.write(f"**Tags:** {tags_to_string(record.tags)}")
                
                with col2:
                    if st.button(f"Edit", key=f"edit_dash_{record.id}"):
                        st.session_state.editing_record = record.id
                        st.rerun()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Add Condition", use_container_width=True):
            st.session_state.current_page = "My Conditions"
            st.rerun()
    
    with col2:
        if st.button("Add Record", use_container_width=True):
            st.session_state.current_page = "Add New Record"
            st.rerun()
    
    with col3:
        unlinked_count = len(manager.get_unlinked_records())
        if unlinked_count > 0:
            if st.button(f"Link Records ({unlinked_count})", use_container_width=True):
                st.session_state.current_page = "Unlinked Records"
                st.rerun()
        else:
            st.button("All Records Linked ✓", use_container_width=True, disabled=True)

def show_conditions_page():
    st.header("🏥 My Health Conditions")
    
    manager = st.session_state.health_manager
    conditions = manager.get_all_conditions()
    
    # Add new condition button
    if st.button("➕ Add New Condition", type="primary"):
        st.session_state.editing_condition = "new"
        st.rerun()
    
    st.markdown("---")
    
    # Show existing conditions
    if conditions:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox(
                "Filter by Status:",
                ["All", "Active", "Resolved", "Chronic", "Monitoring"]
            )
        with col2:
            severity_filter = st.selectbox(
                "Filter by Severity:",
                ["All", "Mild", "Moderate", "Severe"]
            )
        
        # Filter conditions
        filtered_conditions = conditions.copy()
        if status_filter != "All":
            filtered_conditions = [c for c in filtered_conditions if c.status.lower() == status_filter.lower()]
        if severity_filter != "All":
            filtered_conditions = [c for c in filtered_conditions if c.severity.lower() == severity_filter.lower()]
        
        # Display conditions
        for condition in filtered_conditions:
            with st.expander(f"{condition.name} - {condition.status.title()}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    display_condition_status_badge(condition.status)
                    display_severity_badge(condition.severity)
                    st.write(f"**Description:** {condition.description}")
                    if condition.diagnosed_date:
                        st.write(f"**Diagnosed:** {format_date_only(condition.diagnosed_date)}")
                    if condition.tags:
                        st.write(f"**Tags:** {tags_to_string(condition.tags)}")
                    
                    # Show related records
                    related_records = manager.get_records_by_condition(condition.id)
                    st.write(f"**Related Records:** {len(related_records)}")
                    if related_records:
                        for record in related_records:
                            info = get_record_type_info(record.category)
                            st.write(f"• {info['icon']} {record.title} ({format_date_only(record.date)})")
                
                with col2:
                    if st.button(f"Edit", key=f"edit_condition_{condition.id}"):
                        st.session_state.editing_condition = condition.id
                        st.rerun()
                    
                    if st.button(f"Delete", key=f"delete_condition_{condition.id}"):
                        if st.session_state.get(f"confirm_delete_condition_{condition.id}"):
                            manager.delete_condition(condition.id)
                            st.success("Condition deleted successfully!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_condition_{condition.id}"] = True
                            st.warning("Click delete again to confirm")
    
    else:
        st.info("No conditions added yet. Add your first condition to start organizing your health records!")

def show_add_record_form():
    st.header("➕ Add New Health Record")
    
    # First, let user select the type of record they want to add
    if 'selected_record_type' not in st.session_state:
        st.session_state.selected_record_type = None
    
    if st.session_state.selected_record_type is None:
        show_record_type_selection()
    else:
        show_specialized_form(st.session_state.selected_record_type)

def show_unlinked_records():
    st.header("⚠️ Unlinked Records")
    st.info("These records are not linked to any condition. Link them to organize your health data better!")
    
    manager = st.session_state.health_manager
    unlinked_records = manager.get_unlinked_records()
    conditions = manager.get_all_conditions()
    
    if not unlinked_records:
        st.success("🎉 All records are linked to conditions!")
        if st.button("Back to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    # Group unlinked records by category
    categories = {}
    for record in unlinked_records:
        if record.category not in categories:
            categories[record.category] = []
        categories[record.category].append(record)
    
    # Display by category
    for category, records in categories.items():
        with st.expander(f"{get_record_type_info(category)['icon']} {category.title()} ({len(records)} records)"):
            for record in records:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    display_category_badge(record.category)
                    display_unlinked_badge()
                    st.write(f"**{record.title}** - {format_date_only(record.date)}")
                    st.write(f"**Description:** {truncate_text(record.description, 100)}")
                    if record.tags:
                        st.write(f"**Tags:** {tags_to_string(record.tags)}")
                
                with col2:
                    # Link to condition dropdown
                    if conditions:
                        condition_options = {c.id: c.name for c in conditions}
                        condition_options[""] = "Select a condition..."
                        
                        selected_condition = st.selectbox(
                            "Link to condition:",
                            options=list(condition_options.keys()),
                            format_func=lambda x: condition_options[x],
                            key=f"link_{record.id}"
                        )
                        
                        if selected_condition and st.button(f"Link", key=f"link_btn_{record.id}"):
                            if manager.link_record_to_condition(record.id, selected_condition):
                                st.success("Record linked successfully!")
                                st.rerun()
                    else:
                        st.write("No conditions available")
                        if st.button(f"Create Condition", key=f"create_condition_{record.id}"):
                            st.session_state.current_page = "My Conditions"
                            st.rerun()

def show_record_type_selection():
    st.markdown("### What would you like to track today?")
    st.markdown("Choose the type of health information you want to add:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Medication
        if st.button("💊 Medication", use_container_width=True):
            st.session_state.selected_record_type = "medication"
            st.rerun()
        st.markdown("*Track medications, dosages, and schedules*")
        
        # Symptoms
        if st.button("🤒 Symptoms", use_container_width=True):
            st.session_state.selected_record_type = "symptoms"
            st.rerun()
        st.markdown("*Log symptoms and their severity*")
        
        # Health Analysis/Tests
        if st.button("🔬 Health Analysis", use_container_width=True):
            st.session_state.selected_record_type = "analysis"
            st.rerun()
        st.markdown("*Record test results and health measurements*")
    
    with col2:
        # Appointment
        if st.button("👩‍⚕️ Appointment", use_container_width=True):
            st.session_state.selected_record_type = "appointment"
            st.rerun()
        st.markdown("*Schedule or record medical appointments*")
        
        # Daily Note
        if st.button("📝 Daily Note", use_container_width=True):
            st.session_state.selected_record_type = "daily_note"
            st.rerun()
        st.markdown("*General health notes and observations*")
        
        # Treatment
        if st.button("🏥 Treatment", use_container_width=True):
            st.session_state.selected_record_type = "treatment"
            st.rerun()
        st.markdown("*Track treatments and procedures*")

def show_specialized_form(record_type):
    # Back button
    if st.button("← Back to selection"):
        st.session_state.selected_record_type = None
        st.rerun()
    
    st.markdown("---")
    
    if record_type == "medication":
        show_medication_form()
    elif record_type == "symptoms":
        show_symptoms_form()
    elif record_type == "analysis":
        show_analysis_form()
    elif record_type == "appointment":
        show_appointment_form()
    elif record_type == "daily_note":
        show_daily_note_form()
    elif record_type == "treatment":
        show_treatment_form()

def show_medication_form():
    st.header("💊 Add Medication")
    
    # Ask about relationship first
    manager = st.session_state.health_manager
    conditions = manager.get_all_conditions()
    
    if conditions:
        st.markdown("### 🔗 Link to Condition")
        st.info("Is this medication for treating an existing condition?")
        
        condition_options = {c.id: f"{c.name} ({c.status})" for c in conditions}
        condition_options[""] = "None - this is not related to a specific condition"
        condition_options["new"] = "➕ Create a new condition"
        
        selected_condition = st.selectbox(
            "Link to condition:",
            options=list(condition_options.keys()),
            format_func=lambda x: condition_options[x],
            key="medication_condition_link"
        )
        
        if selected_condition == "new":
            st.info("After adding this medication, you'll be prompted to create a new condition.")
        elif selected_condition:
            condition = manager.get_condition(selected_condition)
            if condition:
                st.success(f"✅ This medication will be linked to: **{condition.name}**")
        
        st.markdown("---")
    
    with st.form("medication_form"):
        # Medication-specific fields
        col1, col2 = st.columns(2)
        
        with col1:
            medication_name = st.text_input("Medication Name*", placeholder="e.g., Aspirin")
            dosage = st.text_input("Dosage*", placeholder="e.g., 100mg")
            frequency = st.selectbox("Frequency*", ["Once daily", "Twice daily", "Three times daily", "Four times daily", "As needed", "Other"])
            start_date = st.date_input("Start Date*", value=date.today())
        
        with col2:
            doctor_name = st.text_input("Prescribed by", placeholder="Dr. Smith")
            end_date = st.date_input("End Date (if applicable)", value=None)
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., blood pressure, heart")
        
        # Additional details
        reason = st.text_area("Reason for medication*", placeholder="What is this medication for?", height=80)
        side_effects = st.text_area("Side effects (if any)", placeholder="Any side effects experienced?", height=68)
        notes = st.text_area("Additional notes", placeholder="Any other relevant information...", height=68)
        
        # File upload
        st.markdown("### 📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload prescription or related documents",
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Save Medication")
        
        if submitted:
            if not medication_name or not dosage or not reason:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Process uploaded files
            attachment_paths = []
            if uploaded_files:
                ensure_upload_directory()
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    if file_path:
                        attachment_paths.append(file_path)
                        
                        # Create file attachment record
                        file_attachment = FileAttachment(
                            id=generate_id(),
                            filename=Path(file_path).name,
                            original_name=uploaded_file.name,
                            file_path=file_path,
                            file_type=get_file_type(uploaded_file.name),
                            size=get_file_size(file_path),
                            uploaded_at=get_current_timestamp(),
                            description=f"Attachment for {medication_name}",
                            tags=parse_tags(tags_input)
                        )
                        st.session_state.health_manager.add_attachment(file_attachment)
            
            # Create health record
            full_description = f"Reason: {reason}"
            if side_effects:
                full_description += f"\nSide Effects: {side_effects}"
            if notes:
                full_description += f"\nNotes: {notes}"
            
            metadata = {
                'doctor_name': doctor_name,
                'dosage': dosage,
                'frequency': frequency,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'reason': reason,
                'side_effects': side_effects,
                'notes': notes
            }
            
            # Handle condition linking
            condition_id = None
            if conditions:
                selected_condition = st.session_state.get("medication_condition_link")
                if selected_condition and selected_condition != "new":
                    condition_id = selected_condition
            
            record = HealthRecord(
                id=generate_id(),
                category="medication",
                title=medication_name,
                description=full_description,
                date=start_date.isoformat(),
                tags=parse_tags(tags_input),
                metadata=metadata,
                attachments=attachment_paths,
                condition_id=condition_id,
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            st.session_state.health_manager.add_record(record)
            st.success("✅ Medication record added successfully!")
            
            # Handle new condition creation
            if conditions and st.session_state.get("medication_condition_link") == "new":
                st.info("Now let's create a new condition for this medication.")
                st.session_state.editing_condition = "new"
                st.session_state.current_page = "My Conditions"
                st.session_state.link_record_after_condition = record.id
                st.rerun()
            
            st.balloons()
            st.session_state.selected_record_type = None

def show_symptoms_form():
    st.header("🤒 Add Symptoms")
    
    with st.form("symptoms_form"):
        # Symptoms-specific fields
        col1, col2 = st.columns(2)
        
        with col1:
            symptom_name = st.text_input("Primary Symptom*", placeholder="e.g., Headache")
            severity = st.selectbox("Severity*", ["Mild", "Moderate", "Severe", "Very Severe"])
            onset_date = st.date_input("When did it start?*", value=date.today())
            duration = st.text_input("Duration", placeholder="e.g., 2 hours, 3 days")
        
        with col2:
            location = st.text_input("Location", placeholder="e.g., Left temple")
            frequency = st.selectbox("Frequency", ["First time", "Occasional", "Daily", "Weekly", "Monthly"])
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., stress, weather")
        
        # Additional details
        description = st.text_area("Detailed Description*", placeholder="Describe the symptom in detail...", height=100)
        triggers = st.text_area("Possible Triggers", placeholder="What might have caused this?", height=68)
        relief_measures = st.text_area("What helps/helped?", placeholder="Medications, rest, etc.", height=68)
        
        # File upload
        st.markdown("### 📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload photos or documents",
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Save Symptoms")
        
        if submitted:
            if not symptom_name or not severity or not description:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Process uploaded files
            attachment_paths = []
            if uploaded_files:
                ensure_upload_directory()
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    if file_path:
                        attachment_paths.append(file_path)
                        
                        file_attachment = FileAttachment(
                            id=generate_id(),
                            filename=Path(file_path).name,
                            original_name=uploaded_file.name,
                            file_path=file_path,
                            file_type=get_file_type(uploaded_file.name),
                            size=get_file_size(file_path),
                            uploaded_at=get_current_timestamp(),
                            description=f"Attachment for {symptom_name}",
                            tags=parse_tags(tags_input)
                        )
                        st.session_state.health_manager.add_attachment(file_attachment)
            
            # Create health record
            full_description = f"Description: {description}"
            if triggers:
                full_description += f"\nTriggers: {triggers}"
            if relief_measures:
                full_description += f"\nRelief Measures: {relief_measures}"
            
            metadata = {
                'severity': severity,
                'location': location,
                'duration': duration,
                'frequency': frequency,
                'onset_date': onset_date.isoformat(),
                'triggers': triggers,
                'relief_measures': relief_measures
            }
            
            record = HealthRecord(
                id=generate_id(),
                category="symptoms",
                title=symptom_name,
                description=full_description,
                date=onset_date.isoformat(),
                tags=parse_tags(tags_input),
                metadata=metadata,
                attachments=attachment_paths,
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            st.session_state.health_manager.add_record(record)
            st.success("✅ Symptoms record added successfully!")
            st.balloons()
            st.session_state.selected_record_type = None

def show_analysis_form():
    st.header("🔬 Add Health Analysis")
    
    with st.form("analysis_form"):
        # Analysis-specific fields
        col1, col2 = st.columns(2)
        
        with col1:
            test_name = st.text_input("Test/Analysis Name*", placeholder="e.g., Blood Test")
            test_date = st.date_input("Test Date*", value=date.today())
            provider = st.text_input("Healthcare Provider", placeholder="Dr. Smith / ABC Lab")
        
        with col2:
            category = st.selectbox("Test Category", ["Blood Test", "Urine Test", "Imaging", "Physical Exam", "Other"])
            status = st.selectbox("Status", ["Completed", "Pending", "Scheduled"])
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., routine, annual")
        
        # Results
        results = st.text_area("Results*", placeholder="Enter test results or findings...", height=120)
        reference_values = st.text_area("Reference Values", placeholder="Normal ranges (if applicable)", height=68)
        interpretation = st.text_area("Doctor's Interpretation", placeholder="What do these results mean?", height=80)
        
        # File upload
        st.markdown("### 📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload test results, reports, or images",
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Save Analysis")
        
        if submitted:
            if not test_name or not results:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Process uploaded files
            attachment_paths = []
            if uploaded_files:
                ensure_upload_directory()
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    if file_path:
                        attachment_paths.append(file_path)
                        
                        file_attachment = FileAttachment(
                            id=generate_id(),
                            filename=Path(file_path).name,
                            original_name=uploaded_file.name,
                            file_path=file_path,
                            file_type=get_file_type(uploaded_file.name),
                            size=get_file_size(file_path),
                            uploaded_at=get_current_timestamp(),
                            description=f"Attachment for {test_name}",
                            tags=parse_tags(tags_input)
                        )
                        st.session_state.health_manager.add_attachment(file_attachment)
            
            # Create health record
            full_description = f"Results: {results}"
            if reference_values:
                full_description += f"\nReference Values: {reference_values}"
            if interpretation:
                full_description += f"\nInterpretation: {interpretation}"
            
            metadata = {
                'provider': provider,
                'category': category,
                'status': status,
                'test_date': test_date.isoformat(),
                'results': results,
                'reference_values': reference_values,
                'interpretation': interpretation
            }
            
            record = HealthRecord(
                id=generate_id(),
                category="analysis",
                title=test_name,
                description=full_description,
                date=test_date.isoformat(),
                tags=parse_tags(tags_input),
                metadata=metadata,
                attachments=attachment_paths,
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            st.session_state.health_manager.add_record(record)
            st.success("✅ Health analysis record added successfully!")
            st.balloons()
            st.session_state.selected_record_type = None

def show_appointment_form():
    st.header("👩‍⚕️ Add Appointment")
    
    with st.form("appointment_form"):
        # Appointment-specific fields
        col1, col2 = st.columns(2)
        
        with col1:
            appointment_type = st.selectbox("Appointment Type*", ["Consultation", "Follow-up", "Procedure", "Emergency", "Routine Check", "Other"])
            doctor_name = st.text_input("Doctor/Provider*", placeholder="Dr. Smith")
            appointment_date = st.date_input("Appointment Date*", value=date.today())
            appointment_time = st.time_input("Appointment Time")
        
        with col2:
            clinic_name = st.text_input("Clinic/Hospital", placeholder="ABC Medical Center")
            address = st.text_input("Address", placeholder="123 Main St")
            phone = st.text_input("Phone Number", placeholder="+1 234 567 8900")
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., cardiology, routine")
        
        # Additional details
        reason = st.text_area("Reason for Appointment*", placeholder="What is this appointment for?", height=80)
        preparation = st.text_area("Preparation Required", placeholder="Any special preparation needed?", height=68)
        notes = st.text_area("Additional Notes", placeholder="Any other relevant information...", height=68)
        
        # File upload
        st.markdown("### 📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload appointment confirmation or related documents",
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Save Appointment")
        
        if submitted:
            if not appointment_type or not doctor_name or not reason:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Process uploaded files
            attachment_paths = []
            if uploaded_files:
                ensure_upload_directory()
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    if file_path:
                        attachment_paths.append(file_path)
                        
                        file_attachment = FileAttachment(
                            id=generate_id(),
                            filename=Path(file_path).name,
                            original_name=uploaded_file.name,
                            file_path=file_path,
                            file_type=get_file_type(uploaded_file.name),
                            size=get_file_size(file_path),
                            uploaded_at=get_current_timestamp(),
                            description=f"Attachment for appointment with {doctor_name}",
                            tags=parse_tags(tags_input)
                        )
                        st.session_state.health_manager.add_attachment(file_attachment)
            
            # Create health record
            full_description = f"Reason: {reason}"
            if preparation:
                full_description += f"\nPreparation: {preparation}"
            if notes:
                full_description += f"\nNotes: {notes}"
            
            metadata = {
                'appointment_type': appointment_type,
                'doctor_name': doctor_name,
                'clinic_name': clinic_name,
                'address': address,
                'phone': phone,
                'appointment_date': appointment_date.isoformat(),
                'appointment_time': appointment_time.isoformat() if appointment_time else None,
                'reason': reason,
                'preparation': preparation,
                'notes': notes
            }
            
            record = HealthRecord(
                id=generate_id(),
                category="appointment",
                title=f"{appointment_type} with {doctor_name}",
                description=full_description,
                date=appointment_date.isoformat(),
                tags=parse_tags(tags_input),
                metadata=metadata,
                attachments=attachment_paths,
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            st.session_state.health_manager.add_record(record)
            st.success("✅ Appointment record added successfully!")
            st.balloons()
            st.session_state.selected_record_type = None

def show_daily_note_form():
    st.header("📝 Add Daily Note")
    
    with st.form("daily_note_form"):
        # Daily note fields
        col1, col2 = st.columns(2)
        
        with col1:
            note_date = st.date_input("Date*", value=date.today())
            mood = st.selectbox("Overall Mood", ["Great", "Good", "Okay", "Poor", "Very Poor"])
            energy_level = st.selectbox("Energy Level", ["Very High", "High", "Normal", "Low", "Very Low"])
        
        with col2:
            sleep_quality = st.selectbox("Sleep Quality", ["Excellent", "Good", "Fair", "Poor", "Very Poor"])
            exercise = st.text_input("Exercise/Activity", placeholder="e.g., 30 min walk")
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., stress, work")
        
        # Main content
        notes = st.text_area("Daily Notes*", placeholder="How are you feeling today? Any observations?", height=150)
        
        # File upload
        st.markdown("### 📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload photos or documents",
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Save Daily Note")
        
        if submitted:
            if not notes:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Process uploaded files
            attachment_paths = []
            if uploaded_files:
                ensure_upload_directory()
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    if file_path:
                        attachment_paths.append(file_path)
                        
                        file_attachment = FileAttachment(
                            id=generate_id(),
                            filename=Path(file_path).name,
                            original_name=uploaded_file.name,
                            file_path=file_path,
                            file_type=get_file_type(uploaded_file.name),
                            size=get_file_size(file_path),
                            uploaded_at=get_current_timestamp(),
                            description=f"Attachment for daily note",
                            tags=parse_tags(tags_input)
                        )
                        st.session_state.health_manager.add_attachment(file_attachment)
            
            metadata = {
                'mood': mood,
                'energy_level': energy_level,
                'sleep_quality': sleep_quality,
                'exercise': exercise
            }
            
            record = HealthRecord(
                id=generate_id(),
                category="daily_note",
                title=f"Daily Note - {note_date.strftime('%Y-%m-%d')}",
                description=notes,
                date=note_date.isoformat(),
                tags=parse_tags(tags_input),
                metadata=metadata,
                attachments=attachment_paths,
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            st.session_state.health_manager.add_record(record)
            st.success("✅ Daily note added successfully!")
            st.balloons()
            st.session_state.selected_record_type = None

def show_treatment_form():
    st.header("🏥 Add Treatment")
    
    with st.form("treatment_form"):
        # Treatment-specific fields
        col1, col2 = st.columns(2)
        
        with col1:
            treatment_name = st.text_input("Treatment Name*", placeholder="e.g., Physical Therapy")
            treatment_type = st.selectbox("Treatment Type", ["Physical Therapy", "Surgery", "Procedure", "Therapy", "Other"])
            provider = st.text_input("Healthcare Provider*", placeholder="Dr. Smith")
            treatment_date = st.date_input("Treatment Date*", value=date.today())
        
        with col2:
            location = st.text_input("Location", placeholder="ABC Medical Center")
            duration = st.text_input("Duration", placeholder="e.g., 1 hour, 2 weeks")
            cost = st.text_input("Cost", placeholder="e.g., $200")
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., back pain, rehabilitation")
        
        # Additional details
        description = st.text_area("Treatment Description*", placeholder="What was done?", height=100)
        outcome = st.text_area("Outcome/Results", placeholder="How did it go? Any improvements?", height=80)
        follow_up = st.text_area("Follow-up Required", placeholder="Any follow-up treatments needed?", height=68)
        
        # File upload
        st.markdown("### 📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload treatment reports or related documents",
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Save Treatment")
        
        if submitted:
            if not treatment_name or not provider or not description:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Process uploaded files
            attachment_paths = []
            if uploaded_files:
                ensure_upload_directory()
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    if file_path:
                        attachment_paths.append(file_path)
                        
                        file_attachment = FileAttachment(
                            id=generate_id(),
                            filename=Path(file_path).name,
                            original_name=uploaded_file.name,
                            file_path=file_path,
                            file_type=get_file_type(uploaded_file.name),
                            size=get_file_size(file_path),
                            uploaded_at=get_current_timestamp(),
                            description=f"Attachment for {treatment_name}",
                            tags=parse_tags(tags_input)
                        )
                        st.session_state.health_manager.add_attachment(file_attachment)
            
            # Create health record
            full_description = f"Description: {description}"
            if outcome:
                full_description += f"\nOutcome: {outcome}"
            if follow_up:
                full_description += f"\nFollow-up: {follow_up}"
            
            metadata = {
                'treatment_type': treatment_type,
                'provider': provider,
                'location': location,
                'duration': duration,
                'cost': cost,
                'treatment_date': treatment_date.isoformat(),
                'outcome': outcome,
                'follow_up': follow_up
            }
            
            record = HealthRecord(
                id=generate_id(),
                category="treatment",
                title=treatment_name,
                description=full_description,
                date=treatment_date.isoformat(),
                tags=parse_tags(tags_input),
                metadata=metadata,
                attachments=attachment_paths,
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            st.session_state.health_manager.add_record(record)
            st.success("✅ Treatment record added successfully!")
            st.balloons()
            st.session_state.selected_record_type = None

def show_all_records():
    st.header("📋 All Health Records")
    
    manager = st.session_state.health_manager
    records = manager.get_all_records()
    
    if not records:
        st.info("No health records found. Add your first record to get started!")
        return
    
    # Sort options
    col1, col2 = st.columns([1, 3])
    with col1:
        sort_by = st.selectbox(
            "Sort by:",
            ["Date (newest first)", "Date (oldest first)", "Title", "Category"]
        )
    
    # Sort records
    if sort_by == "Date (newest first)":
        records = sorted(records, key=lambda x: x.date, reverse=True)
    elif sort_by == "Date (oldest first)":
        records = sorted(records, key=lambda x: x.date)
    elif sort_by == "Title":
        records = sorted(records, key=lambda x: x.title.lower())
    elif sort_by == "Category":
        records = sorted(records, key=lambda x: x.category)
    
    # Display records
    for record in records:
        with st.expander(f"{record.title} - {format_date(record.date)}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                display_category_badge(record.category)
                
                # Show condition link status
                if record.condition_id:
                    display_linked_badge()
                    condition = manager.get_condition(record.condition_id)
                    if condition:
                        st.write(f"**Linked to:** {condition.name}")
                else:
                    display_unlinked_badge()
                
                st.write(f"**Date:** {format_date(record.date)}")
                st.write(f"**Description:** {record.description}")
                
                if record.tags:
                    st.write(f"**Tags:** {tags_to_string(record.tags)}")
                
                # Show metadata
                if any(record.metadata.values()):
                    st.markdown("**Additional Information:**")
                    for key, value in record.metadata.items():
                        if value:
                            st.write(f"• {key.replace('_', ' ').title()}: {value}")
                
                # Show attachments
                if record.attachments:
                    st.markdown("**Attachments:**")
                    for attachment_path in record.attachments:
                        if os.path.exists(attachment_path):
                            file_size = format_file_size(get_file_size(attachment_path))
                            st.write(f"📎 {Path(attachment_path).name} ({file_size})")
            
            with col2:
                if st.button(f"Edit", key=f"edit_all_{record.id}"):
                    st.session_state.editing_record = record.id
                    st.rerun()
                
                if st.button(f"Delete", key=f"delete_all_{record.id}"):
                    if st.session_state.get(f"confirm_delete_all_{record.id}"):
                        manager.delete_record(record.id)
                        st.success("Record deleted successfully!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_all_{record.id}"] = True
                        st.warning("Click delete again to confirm")

def show_search_records():
    st.header("🔍 Search Health Records")
    
    manager = st.session_state.health_manager
    
    # Search filters
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input(
            "Search in title and description:",
            placeholder="Enter keywords..."
        )
        
    with col2:
        category_filter = st.selectbox(
            "Filter by category:",
            ["All"] + ["medication", "treatment", "diagnosis", "daily_note", "appointment", "symptoms", "analysis"]
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        tags_filter = st.text_input(
            "Filter by tags (comma-separated):",
            placeholder="e.g., blood pressure, routine"
        )
    
    with col2:
        # Condition filter
        conditions = manager.get_all_conditions()
        condition_options = ["All", "Unlinked"] + [c.name for c in conditions]
        condition_filter = st.selectbox(
            "Filter by condition:",
            condition_options
        )
    
    # Perform search
    category = None if category_filter == "All" else category_filter
    tags = parse_tags(tags_filter) if tags_filter else None
    
    # Handle condition filtering
    condition_id = None
    if condition_filter != "All":
        if condition_filter == "Unlinked":
            # Special case: show only unlinked records
            results = manager.search_records(query=search_query, category=category, tags=tags)
            results = [r for r in results if not r.condition_id]
        else:
            # Find condition by name
            condition = next((c for c in conditions if c.name == condition_filter), None)
            if condition:
                condition_id = condition.id
                results = manager.search_records(
                    query=search_query,
                    category=category,
                    tags=tags,
                    condition_id=condition_id
                )
            else:
                results = []
    else:
        results = manager.search_records(
            query=search_query,
            category=category,
            tags=tags
        )
    
    st.markdown(f"### Found {len(results)} record(s)")
    
    if results:
        for record in results:
            with st.expander(f"{record.title} - {format_date(record.date)}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    display_category_badge(record.category)
                    
                    # Show condition link status
                    if record.condition_id:
                        display_linked_badge()
                        condition = manager.get_condition(record.condition_id)
                        if condition:
                            st.write(f"**Linked to:** {condition.name}")
                    else:
                        display_unlinked_badge()
                    
                    st.write(f"**Date:** {format_date(record.date)}")
                    st.write(f"**Description:** {truncate_text(record.description, 150)}")
                    
                    if record.tags:
                        st.write(f"**Tags:** {tags_to_string(record.tags)}")
                
                with col2:
                    if st.button(f"View Details", key=f"view_{record.id}"):
                        st.session_state.editing_record = record.id
                        st.rerun()
    else:
        st.info("No records found matching your search criteria.")

# Handle condition editing
if st.session_state.editing_condition:
    condition_id = st.session_state.editing_condition
    
    if condition_id == "new":
        st.markdown("---")
        st.header("➕ Add New Condition")
        
        with st.form("add_condition_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                condition_name = st.text_input("Condition Name*", placeholder="e.g., Hypertension")
                status = st.selectbox("Status*", ["active", "resolved", "chronic", "monitoring"])
                severity = st.selectbox("Severity*", ["mild", "moderate", "severe"])
                diagnosed_date = st.date_input("Diagnosed Date", value=None)
            
            with col2:
                category = st.selectbox("Category", get_condition_categories())
                tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., heart, blood pressure")
            
            description = st.text_area("Description*", placeholder="Describe the condition...", height=100)
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Add Condition")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.editing_condition = None
                    st.rerun()
            
            if submitted:
                if not condition_name or not description:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    condition = Condition(
                        id=generate_id(),
                        name=condition_name,
                        description=description,
                        diagnosed_date=diagnosed_date.isoformat() if diagnosed_date else None,
                        status=status,
                        severity=severity,
                        tags=parse_tags(tags_input),
                        created_at=get_current_timestamp(),
                        updated_at=get_current_timestamp()
                    )
                    
                    st.session_state.health_manager.add_condition(condition)
                    st.success("✅ Condition added successfully!")
                    
                    # Handle linking record after condition creation
                    if 'link_record_after_condition' in st.session_state:
                        record_id = st.session_state.link_record_after_condition
                        st.session_state.health_manager.link_record_to_condition(record_id, condition.id)
                        st.success("✅ Record linked to new condition!")
                        del st.session_state.link_record_after_condition
                    
                    st.session_state.editing_condition = None
                    st.rerun()
    
    else:
        condition = st.session_state.health_manager.get_condition(condition_id)
        
        if condition:
            st.markdown("---")
            st.header("✏️ Edit Condition")
            
            with st.form("edit_condition_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    condition_name = st.text_input("Condition Name*", value=condition.name)
                    status = st.selectbox("Status*", ["active", "resolved", "chronic", "monitoring"], 
                                        index=["active", "resolved", "chronic", "monitoring"].index(condition.status))
                    severity = st.selectbox("Severity*", ["mild", "moderate", "severe"],
                                          index=["mild", "moderate", "severe"].index(condition.severity))
                    diagnosed_date = st.date_input("Diagnosed Date", 
                                                 value=datetime.fromisoformat(condition.diagnosed_date).date() if condition.diagnosed_date else None)
                
                with col2:
                    tags_input = st.text_input("Tags (comma-separated)", value=tags_to_string(condition.tags))
                
                description = st.text_area("Description*", value=condition.description, height=100)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    submitted = st.form_submit_button("Update Condition")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.editing_condition = None
                        st.rerun()
                
                if submitted:
                    if not condition_name or not description:
                        st.error("Please fill in all required fields (marked with *)")
                    else:
                        updated_condition = Condition(
                            id=condition.id,
                            name=condition_name,
                            description=description,
                            diagnosed_date=diagnosed_date.isoformat() if diagnosed_date else None,
                            status=status,
                            severity=severity,
                            tags=parse_tags(tags_input),
                            created_at=condition.created_at,
                            updated_at=get_current_timestamp()
                        )
                        
                        st.session_state.health_manager.update_condition(condition_id, updated_condition)
                        st.success("✅ Condition updated successfully!")
                        st.session_state.editing_condition = None
                        st.rerun()

# Handle editing
if st.session_state.editing_record:
    record_id = st.session_state.editing_record
    record = st.session_state.health_manager.get_record(record_id)
    
    if record:
        st.markdown("---")
        st.header("✏️ Edit Health Record")
        
        with st.form("edit_record_form"):
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title*", value=record.title)
                category = st.selectbox(
                    "Category*",
                    ["medication", "treatment", "diagnosis", "daily_note", "appointment", "symptoms", "analysis"],
                    index=["medication", "treatment", "diagnosis", "daily_note", "appointment", "symptoms", "analysis"].index(record.category)
                )
                record_date = st.date_input("Date*", value=datetime.fromisoformat(record.date).date())
            
            with col2:
                tags_input = st.text_input(
                    "Tags (comma-separated)",
                    value=tags_to_string(record.tags)
                )
                
                # Condition linking
                conditions = st.session_state.health_manager.get_all_conditions()
                if conditions:
                    condition_options = {c.id: c.name for c in conditions}
                    condition_options[""] = "Not linked to any condition"
                    
                    current_condition = record.condition_id if record.condition_id else ""
                    
                    selected_condition = st.selectbox(
                        "Linked Condition:",
                        options=list(condition_options.keys()),
                        format_func=lambda x: condition_options[x],
                        index=list(condition_options.keys()).index(current_condition) if current_condition in condition_options else 0
                    )
            
            description = st.text_area(
                "Description*",
                value=record.description,
                height=100
            )
            
            # Additional metadata
            with st.expander("Additional Information"):
                col1, col2 = st.columns(2)
                with col1:
                    doctor_name = st.text_input("Doctor/Provider Name", value=record.metadata.get('doctor_name', ''))
                    location = st.text_input("Location/Clinic", value=record.metadata.get('location', ''))
                with col2:
                    dosage = st.text_input("Dosage (for medications)", value=record.metadata.get('dosage', ''))
                    follow_up = st.text_input("Follow-up Required", value=record.metadata.get('follow_up', ''))
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Update Record")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.editing_record = None
                    st.rerun()
            
            if submitted:
                if not title or not description:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    # Update record
                    metadata = {
                        'doctor_name': doctor_name,
                        'location': location,
                        'dosage': dosage,
                        'follow_up': follow_up
                    }
                    
                    # Handle condition linking
                    condition_id = None
                    if conditions:
                        condition_id = selected_condition if selected_condition else None
                    
                    updated_record = HealthRecord(
                        id=record.id,
                        category=category,
                        title=title,
                        description=description,
                        date=record_date.isoformat(),
                        tags=parse_tags(tags_input),
                        metadata=metadata,
                        attachments=record.attachments,
                        condition_id=condition_id,
                        created_at=record.created_at,
                        updated_at=get_current_timestamp()
                    )
                    
                    st.session_state.health_manager.update_record(record_id, updated_record)
                    st.success("✅ Record updated successfully!")
                    st.session_state.editing_record = None
                    st.rerun()

if __name__ == "__main__":
    main() 