"""
Athena Query Tools

This module provides Agno tools for querying the AWS Athena catalog service
to retrieve structured information about projects, contacts, and services.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Union

from agno import tool
from pydantic import BaseModel, Field

from ..config import get_config
from ..libs.aws_clients import get_aws_clients
from ..libs.project_manager import get_project_manager
from ..models import RetrievalResult, SourceType

logger = logging.getLogger(__name__)


class AthenaQueryResult(BaseModel):
    """Result from Athena query execution"""
    success: bool = Field(..., description="Whether the query was successful")
    query: Optional[str] = Field(None, description="The SQL query that was executed")
    results: List[Dict] = Field(default_factory=list, description="Query results as list of dicts")
    formatted_content: str = Field(default="", description="Formatted content for context")
    execution_time: float = Field(..., description="Time taken for query execution")
    row_count: int = Field(default=0, description="Number of rows returned")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class AthenaQueryCategories:
    """Categories for different types of Athena queries"""
    PROJECT_DETAILS = "PROJECT_DETAILS"
    SPECIFIC_CONTACT = "SPECIFIC_CONTACT"
    FIND_PROJECT_BY_PERSON = "FIND_PROJECT_BY_PERSON"
    MULTI_PROJECT_ATTRIBUTE_SEARCH = "MULTI_PROJECT_ATTRIBUTE_SEARCH"
    MULTI_PROJECT_LIST_ALL = "MULTI_PROJECT_LIST_ALL"
    MULTI_PROJECT_FIND_PROJECTS_BY_ATTRIBUTE = "MULTI_PROJECT_FIND_PROJECTS_BY_ATTRIBUTE"
    MULTI_PROJECT_FIND_PERSON_BY_ROLE = "MULTI_PROJECT_FIND_PERSON_BY_ROLE"
    NO_ATHENA_QUERY = "NO_ATHENA_QUERY"


@tool
def query_project_details(
    project_name: str,
    specific_fields: Optional[List[str]] = None
) -> AthenaQueryResult:
    """
    Query detailed information about a specific project from the catalog.
    
    Args:
        project_name: Name of the project to query
        specific_fields: Optional list of specific fields to retrieve
        
    Returns:
        AthenaQueryResult with project details
    """
    start_time = time.time()
    config = get_config()
    aws_clients = get_aws_clients()
    project_manager = get_project_manager()
    
    logger.info(f"Querying project details for: {project_name}")
    
    try:
        # Validate and normalize project name
        canonical_project = project_manager.get_canonical_name(project_name)
        if not canonical_project:
            error_msg = f"Project '{project_name}' not found in project manager"
            logger.warning(error_msg)
            return AthenaQueryResult(
                success=False,
                error_message=error_msg,
                execution_time=time.time() - start_time
            )
        
        # Build SQL query
        if specific_fields:
            fields = ", ".join(_sql_safe_quote(field) for field in specific_fields)
        else:
            fields = "*"
        
        query = f"""
        SELECT {fields}
        FROM {config.athena_database}.{config.athena_table}
        WHERE elemName = '{_sql_safe_quote(canonical_project)}'
        """
        
        # Execute query
        result = _execute_athena_query(query)
        
        if result.success and result.results:
            # Format the results
            formatted_content = _format_project_details(result.results[0], canonical_project)
            
            return AthenaQueryResult(
                success=True,
                query=query,
                results=result.results,
                formatted_content=formatted_content,
                execution_time=time.time() - start_time,
                row_count=len(result.results)
            )
        else:
            return AthenaQueryResult(
                success=False,
                query=query,
                error_message=result.error_message or "No results found",
                execution_time=time.time() - start_time
            )
    
    except Exception as e:
        error_msg = f"Error querying project details: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return AthenaQueryResult(
            success=False,
            error_message=error_msg,
            execution_time=time.time() - start_time
        )


@tool
def query_project_contacts(
    project_name: str,
    contact_types: Optional[List[str]] = None
) -> AthenaQueryResult:
    """
    Query contact information for a specific project.
    
    Args:
        project_name: Name of the project
        contact_types: Optional list of contact types to filter (e.g., ['CHANGE MANAGER', 'SPONSOR'])
        
    Returns:
        AthenaQueryResult with contact information
    """
    start_time = time.time()
    config = get_config()
    project_manager = get_project_manager()
    
    logger.info(f"Querying contacts for project: {project_name}")
    
    try:
        # Validate project name
        canonical_project = project_manager.get_canonical_name(project_name)
        if not canonical_project:
            error_msg = f"Project '{project_name}' not found"
            return AthenaQueryResult(
                success=False,
                error_message=error_msg,
                execution_time=time.time() - start_time
            )
        
        # Build SQL query to get contacts
        query = f"""
        SELECT elemName, elemCode, listContatti
        FROM {config.athena_database}.{config.athena_table}
        WHERE elemName = '{_sql_safe_quote(canonical_project)}'
        """
        
        # Execute query
        result = _execute_athena_query(query)
        
        if result.success and result.results:
            # Parse and format contacts
            project_data = result.results[0]
            contacts_str = project_data.get('listContatti', '[]')
            
            try:
                contacts = json.loads(contacts_str) if contacts_str else []
            except json.JSONDecodeError:
                contacts = []
            
            # Filter by contact types if specified
            if contact_types:
                contacts = [
                    contact for contact in contacts 
                    if contact.get('role') in contact_types
                ]
            
            formatted_content = _format_project_contacts(contacts, canonical_project)
            
            return AthenaQueryResult(
                success=True,
                query=query,
                results=[{"contacts": contacts}],
                formatted_content=formatted_content,
                execution_time=time.time() - start_time,
                row_count=len(contacts)
            )
        else:
            return AthenaQueryResult(
                success=False,
                query=query,
                error_message="No project data found",
                execution_time=time.time() - start_time
            )
    
    except Exception as e:
        error_msg = f"Error querying project contacts: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return AthenaQueryResult(
            success=False,
            error_message=error_msg,
            execution_time=time.time() - start_time
        )


@tool
def find_projects_by_person(
    person_name: str,
    role: Optional[str] = None
) -> AthenaQueryResult:
    """
    Find all projects where a specific person has a role.
    
    Args:
        person_name: Name of the person to search for
        role: Optional specific role to filter by
        
    Returns:
        AthenaQueryResult with projects where the person is involved
    """
    start_time = time.time()
    config = get_config()
    
    logger.info(f"Finding projects for person: {person_name}")
    
    try:
        # Build SQL query to search in contacts
        query = f"""
        SELECT elemName, elemCode, listContatti
        FROM {config.athena_database}.{config.athena_table}
        WHERE listContatti LIKE '%{_sql_safe_quote(person_name)}%'
        """
        
        # Execute query
        result = _execute_athena_query(query)
        
        if result.success:
            # Parse results to find exact matches
            matching_projects = []
            
            for project_data in result.results:
                contacts_str = project_data.get('listContatti', '[]')
                try:
                    contacts = json.loads(contacts_str) if contacts_str else []
                except json.JSONDecodeError:
                    continue
                
                # Check if person is in contacts
                person_contacts = []
                for contact in contacts:
                    contact_name = contact.get('name', '').lower()
                    contact_role = contact.get('role', '')
                    
                    if person_name.lower() in contact_name:
                        if not role or role.upper() == contact_role.upper():
                            person_contacts.append(contact)
                
                if person_contacts:
                    matching_projects.append({
                        'project': project_data['elemName'],
                        'project_code': project_data.get('elemCode', ''),
                        'roles': person_contacts
                    })
            
            formatted_content = _format_person_projects(matching_projects, person_name, role)
            
            return AthenaQueryResult(
                success=True,
                query=query,
                results=matching_projects,
                formatted_content=formatted_content,
                execution_time=time.time() - start_time,
                row_count=len(matching_projects)
            )
        else:
            return AthenaQueryResult(
                success=False,
                query=query,
                error_message=result.error_message,
                execution_time=time.time() - start_time
            )
    
    except Exception as e:
        error_msg = f"Error finding projects by person: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return AthenaQueryResult(
            success=False,
            error_message=error_msg,
            execution_time=time.time() - start_time
        )


@tool
def find_projects_by_status(status: str) -> AthenaQueryResult:
    """
    Find all projects with a specific status.
    
    Args:
        status: Status to search for (e.g., 'ATTIVO', 'DISMESSO')
        
    Returns:
        AthenaQueryResult with projects matching the status
    """
    start_time = time.time()
    config = get_config()
    
    logger.info(f"Finding projects with status: {status}")
    
    try:
        query = f"""
        SELECT elemName, elemCode, descStatus, descCustomerService
        FROM {config.athena_database}.{config.athena_table}
        WHERE descStatus = '{_sql_safe_quote(status)}'
        ORDER BY elemName
        """
        
        result = _execute_athena_query(query)
        
        if result.success:
            formatted_content = _format_projects_by_attribute(result.results, "status", status)
            
            return AthenaQueryResult(
                success=True,
                query=query,
                results=result.results,
                formatted_content=formatted_content,
                execution_time=time.time() - start_time,
                row_count=len(result.results)
            )
        else:
            return AthenaQueryResult(
                success=False,
                query=query,
                error_message=result.error_message,
                execution_time=time.time() - start_time
            )
    
    except Exception as e:
        error_msg = f"Error finding projects by status: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return AthenaQueryResult(
            success=False,
            error_message=error_msg,
            execution_time=time.time() - start_time
        )


def _execute_athena_query(query: str) -> AthenaQueryResult:
    """Execute an Athena query and return formatted results"""
    start_time = time.time()
    config = get_config()
    aws_clients = get_aws_clients()
    
    try:
        logger.debug(f"Executing Athena query: {query[:200]}...")
        
        # Start query execution
        query_execution_id = aws_clients.start_athena_query(
            query=query,
            database=config.athena_database,
            output_location=config.athena_s3_output_location
        )
        
        if not query_execution_id:
            return AthenaQueryResult(
                success=False,
                error_message="Failed to start Athena query",
                execution_time=time.time() - start_time
            )
        
        # Poll for completion
        max_attempts = 10
        for attempt in range(max_attempts):
            status = aws_clients.get_athena_query_status(query_execution_id)
            
            if status == "SUCCEEDED":
                break
            elif status in ["FAILED", "CANCELLED"]:
                return AthenaQueryResult(
                    success=False,
                    error_message=f"Query {status.lower()}",
                    execution_time=time.time() - start_time
                )
            elif status == "RUNNING":
                time.sleep(3)  # Wait 3 seconds before next poll
            else:
                return AthenaQueryResult(
                    success=False,
                    error_message=f"Unknown query status: {status}",
                    execution_time=time.time() - start_time
                )
        else:
            return AthenaQueryResult(
                success=False,
                error_message="Query timed out",
                execution_time=time.time() - start_time
            )
        
        # Get results
        response = aws_clients.get_athena_query_results(query_execution_id)
        if not response:
            return AthenaQueryResult(
                success=False,
                error_message="Failed to get query results",
                execution_time=time.time() - start_time
            )
        
        # Parse results
        results = []
        result_set = response.get('ResultSet', {})
        rows = result_set.get('Rows', [])
        
        if len(rows) > 1:  # Skip header row
            # Get column names from header
            header_row = rows[0]
            columns = [col.get('VarCharValue', '') for col in header_row.get('Data', [])]
            
            # Parse data rows
            for row in rows[1:]:
                row_data = {}
                data = row.get('Data', [])
                for i, col_name in enumerate(columns):
                    if i < len(data):
                        value = data[i].get('VarCharValue', '')
                        row_data[col_name] = value
                results.append(row_data)
        
        logger.info(f"Athena query returned {len(results)} rows")
        
        return AthenaQueryResult(
            success=True,
            results=results,
            execution_time=time.time() - start_time,
            row_count=len(results)
        )
    
    except Exception as e:
        error_msg = f"Error executing Athena query: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return AthenaQueryResult(
            success=False,
            error_message=error_msg,
            execution_time=time.time() - start_time
        )


def _sql_safe_quote(value: str) -> str:
    """Make a string safe for SQL by escaping single quotes"""
    return value.replace("'", "''")


def _format_project_details(project_data: Dict, project_name: str) -> str:
    """Format project details for context"""
    sections = [
        f"Project Details for: {project_name}",
        "=" * 50,
        ""
    ]
    
    # Basic information
    if 'elemCode' in project_data:
        sections.append(f"Project Code: {project_data['elemCode']}")
    if 'descStatus' in project_data:
        sections.append(f"Status: {project_data['descStatus']}")
    if 'descCustomerService' in project_data:
        sections.append(f"Customer Service: {project_data['descCustomerService']}")
    if 'descServizio' in project_data:
        sections.append(f"Description: {project_data['descServizio']}")
    if 'dataUltimoAggiornamento' in project_data:
        sections.append(f"Last Updated: {project_data['dataUltimoAggiornamento']}")
    
    sections.append("")
    
    # Contacts
    if 'listContatti' in project_data:
        try:
            contacts = json.loads(project_data['listContatti'])
            if contacts:
                sections.append("Contacts:")
                for contact in contacts:
                    name = contact.get('name', 'N/A')
                    role = contact.get('role', 'N/A')
                    email = contact.get('email', 'N/A')
                    sections.append(f"  - {role}: {name} ({email})")
        except json.JSONDecodeError:
            pass
    
    return "\n".join(sections)


def _format_project_contacts(contacts: List[Dict], project_name: str) -> str:
    """Format project contacts for context"""
    sections = [
        f"Contacts for Project: {project_name}",
        "=" * 50,
        ""
    ]
    
    if not contacts:
        sections.append("No contacts found for this project.")
    else:
        for contact in contacts:
            name = contact.get('name', 'N/A')
            role = contact.get('role', 'N/A')
            email = contact.get('email', 'N/A')
            sections.append(f"Role: {role}")
            sections.append(f"Name: {name}")
            sections.append(f"Email: {email}")
            sections.append("")
    
    return "\n".join(sections)


def _format_person_projects(projects: List[Dict], person_name: str, role: Optional[str]) -> str:
    """Format projects where a person is involved"""
    sections = [
        f"Projects involving: {person_name}",
        f"Role filter: {role or 'Any role'}",
        "=" * 50,
        ""
    ]
    
    if not projects:
        sections.append("No projects found for this person.")
    else:
        for project in projects:
            sections.append(f"Project: {project['project']}")
            if project.get('project_code'):
                sections.append(f"Code: {project['project_code']}")
            
            sections.append("Roles:")
            for contact in project['roles']:
                role_name = contact.get('role', 'N/A')
                email = contact.get('email', 'N/A')
                sections.append(f"  - {role_name} ({email})")
            sections.append("")
    
    return "\n".join(sections)


def _format_projects_by_attribute(projects: List[Dict], attribute: str, value: str) -> str:
    """Format projects filtered by an attribute"""
    sections = [
        f"Projects with {attribute}: {value}",
        "=" * 50,
        f"Found {len(projects)} projects",
        ""
    ]
    
    for project in projects:
        sections.append(f"- {project.get('elemName', 'N/A')}")
        if project.get('elemCode'):
            sections.append(f"  Code: {project['elemCode']}")
        if project.get('descCustomerService'):
            sections.append(f"  Service: {project['descCustomerService']}")
        sections.append("")
    
    return "\n".join(sections)


class AthenaQueryTool:
    """
    High-level Athena query tool for the agent.
    """
    
    def __init__(self):
        self.config = get_config()
    
    def query_project(self, project_name: str) -> AthenaQueryResult:
        """Query details for a specific project"""
        return query_project_details(project_name)
    
    def query_contacts(self, project_name: str, contact_types: Optional[List[str]] = None) -> AthenaQueryResult:
        """Query contacts for a project"""
        return query_project_contacts(project_name, contact_types)
    
    def find_by_person(self, person_name: str, role: Optional[str] = None) -> AthenaQueryResult:
        """Find projects by person"""
        return find_projects_by_person(person_name, role)
    
    def find_by_status(self, status: str) -> AthenaQueryResult:
        """Find projects by status"""
        return find_projects_by_status(status) 