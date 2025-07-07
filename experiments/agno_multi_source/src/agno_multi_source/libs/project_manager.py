"""
Centralized Project Name Management for Agno Multi-Source System

This module provides a single source of truth for project names across the entire system.
It ensures consistency between different data sources and components.

Adapted from the LangGraph version but simplified for Agno framework.
"""

import json
import logging
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

import boto3
from pydantic import BaseModel

from ..config import get_config
from ..models import ProjectInfo, ProjectNameField

logger = logging.getLogger(__name__)


class ProjectManager:
    """
    Centralized manager for project names across the system.
    Provides validation, normalization, and mapping between different naming conventions.
    """
    
    def __init__(self):
        self.config = get_config()
        self._projects: Dict[str, ProjectInfo] = {}
        self._name_to_canonical: Dict[str, str] = {}  # Maps any name/alias to canonical name
        self._s3_client = boto3.client("s3")
        self._catalog_cache_ttl = 3600  # Cache catalog for 1 hour
        self._last_catalog_fetch = 0
    
    def _fetch_catalog_from_s3(self) -> List[Dict]:
        """Fetch the project catalog from S3"""
        try:
            logger.info(f"Fetching project catalog from s3://{self.config.catalog_s3_bucket}/{self.config.catalog_s3_key}")
            response = self._s3_client.get_object(
                Bucket=self.config.catalog_s3_bucket, 
                Key=self.config.catalog_s3_key
            )
            body = response['Body'].read()
            catalog_data = json.loads(body.decode('utf-8'))
            
            if not isinstance(catalog_data, list):
                logger.error(f"Catalog data is not a list: {type(catalog_data)}")
                return []
            
            logger.info(f"Successfully fetched {len(catalog_data)} project entries from catalog")
            return catalog_data
            
        except Exception as e:
            logger.error(f"Error fetching catalog from S3: {e}")
            return []
    
    def _build_project_mappings(self, catalog_data: List[Dict]):
        """Build internal project mappings from catalog data"""
        self._projects.clear()
        self._name_to_canonical.clear()
        
        for item in catalog_data:
            elem_name = item.get('elemName')
            if not elem_name:
                continue
            
            # Extract other potential names/aliases
            aliases = set()
            
            # Add variations from different fields
            if item.get('elemcode'):
                aliases.add(item['elemcode'])
            
            # Add display name variations
            display_name = elem_name  # Use elemName as display name by default
            
            # Create project info
            project_info = ProjectInfo(
                canonical_name=elem_name,
                display_name=display_name,
                aliases=aliases,
                is_active=True,  # Assume active if in catalog
                metadata=item
            )
            
            # Store in main projects dict
            self._projects[elem_name] = project_info
            
            # Build reverse mapping for all aliases
            for alias in project_info.aliases:
                # Store both exact and lowercase versions for flexible matching
                self._name_to_canonical[alias] = elem_name
                self._name_to_canonical[alias.lower()] = elem_name
        
        logger.info(f"Built mappings for {len(self._projects)} projects with {len(self._name_to_canonical)} total name mappings")
    
    def refresh_catalog(self, force: bool = False) -> bool:
        """Refresh the project catalog from S3"""
        import time
        current_time = time.time()
        
        if not force and (current_time - self._last_catalog_fetch) < self._catalog_cache_ttl:
            logger.debug("Using cached catalog data")
            return True
        
        catalog_data = self._fetch_catalog_from_s3()
        if not catalog_data:
            logger.error("Failed to fetch catalog data")
            return False
        
        self._build_project_mappings(catalog_data)
        self._last_catalog_fetch = current_time
        return True
    
    def get_canonical_name(self, project_name: str) -> Optional[str]:
        """
        Get the canonical project name for any input name/alias.
        Returns None if project not found.
        """
        if not project_name:
            return None
        
        # Ensure catalog is loaded
        if not self._projects:
            self.refresh_catalog()
        
        # Try exact match first
        canonical = self._name_to_canonical.get(project_name)
        if canonical:
            return canonical
        
        # Try lowercase match
        canonical = self._name_to_canonical.get(project_name.lower())
        if canonical:
            return canonical
        
        # Try prefix matching as fallback
        project_lower = project_name.lower().strip('? ')
        candidates = []
        
        for alias, canonical in self._name_to_canonical.items():
            if alias.lower().startswith(project_lower):
                candidates.append(canonical)
        
        # Return unique canonical name if only one match
        unique_candidates = list(set(candidates))
        if len(unique_candidates) == 1:
            logger.info(f"Found project '{project_name}' via prefix match: '{unique_candidates[0]}'")
            return unique_candidates[0]
        elif len(unique_candidates) > 1:
            logger.warning(f"Ambiguous project name '{project_name}'. Multiple matches: {unique_candidates}")
        
        return None
    
    def validate_project_name(self, project_name: str) -> bool:
        """Check if a project name is valid (exists in catalog)"""
        return self.get_canonical_name(project_name) is not None
    
    def get_project_info(self, project_name: str) -> Optional[ProjectInfo]:
        """Get full project information for a project name"""
        canonical = self.get_canonical_name(project_name)
        if canonical:
            return self._projects.get(canonical)
        return None
    
    def get_all_canonical_names(self) -> List[str]:
        """Get list of all canonical project names"""
        if not self._projects:
            self.refresh_catalog()
        return list(self._projects.keys())
    
    def get_active_projects(self) -> List[str]:
        """Get list of all active project canonical names"""
        if not self._projects:
            self.refresh_catalog()
        return [name for name, info in self._projects.items() if info.is_active]
    
    def normalize_for_metadata(self, project_name: str, field_type: ProjectNameField) -> Optional[str]:
        """
        Normalize a project name for use in a specific metadata field.
        This ensures consistency across different components.
        """
        canonical = self.get_canonical_name(project_name)
        if not canonical:
            return None
        
        # For now, we use canonical name for all field types
        # In the future, we could have field-specific transformations
        return canonical
    
    def validate_and_normalize_list(self, project_names: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate and normalize a list of project names.
        Returns (valid_canonical_names, invalid_names)
        """
        valid = []
        invalid = []
        
        for name in project_names:
            canonical = self.get_canonical_name(name)
            if canonical:
                if canonical not in valid:  # Avoid duplicates
                    valid.append(canonical)
            else:
                invalid.append(name)
        
        return valid, invalid
    
    def get_project_filter_dict(self, project_name: str, field_type: ProjectNameField) -> Dict[str, str]:
        """
        Get a filter dictionary for Qdrant queries using the correct field name.
        Returns a simple dict for compatibility with langchain-qdrant.
        """
        canonical = self.get_canonical_name(project_name)
        if not canonical:
            return {}
        
        return {field_type.value: canonical}
    
    def search_projects(self, query: str, limit: int = 10) -> List[str]:
        """
        Search for projects by name/alias with fuzzy matching.
        Returns list of canonical names.
        """
        if not self._projects:
            self.refresh_catalog()
        
        query_lower = query.lower()
        matches = []
        
        # Exact matches first
        for alias, canonical in self._name_to_canonical.items():
            if alias.lower() == query_lower:
                if canonical not in matches:
                    matches.append(canonical)
        
        # Prefix matches second
        for alias, canonical in self._name_to_canonical.items():
            if alias.lower().startswith(query_lower) and canonical not in matches:
                matches.append(canonical)
        
        # Substring matches last
        for alias, canonical in self._name_to_canonical.items():
            if query_lower in alias.lower() and canonical not in matches:
                matches.append(canonical)
        
        return matches[:limit]


# Global singleton instance
_project_manager_instance: Optional[ProjectManager] = None


def get_project_manager() -> ProjectManager:
    """Get or create the global project manager singleton"""
    global _project_manager_instance
    if _project_manager_instance is None:
        _project_manager_instance = ProjectManager()
    return _project_manager_instance


# Convenience functions for common operations
def get_canonical_project_name(project_name: str) -> Optional[str]:
    """Convenience function to get canonical project name"""
    return get_project_manager().get_canonical_name(project_name)


def validate_project_name(project_name: str) -> bool:
    """Convenience function to validate project name"""
    return get_project_manager().validate_project_name(project_name)


def get_all_project_names() -> List[str]:
    """Convenience function to get all canonical project names"""
    return get_project_manager().get_all_canonical_names()


def normalize_project_for_metadata(project_name: str, field_type: ProjectNameField) -> Optional[str]:
    """Convenience function to normalize project name for metadata"""
    return get_project_manager().normalize_for_metadata(project_name, field_type) 