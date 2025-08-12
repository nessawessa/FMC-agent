"""Operation registry for FMC Agent."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class OperationTemplate:
    """Template for an operation with its metadata and command building logic."""
    sheet: str
    name: str
    required_columns: List[str]
    
    def build_command(self, row_data: Dict[str, str]) -> str:
        """Build RV&S CLI command from row data."""
        from .exceptions import OperationBuildError
        
        # Validate required columns are present
        for col in self.required_columns:
            if not row_data.get(col):
                raise OperationBuildError(f"Missing required column '{col}' for operation '{self.name}'")
        
        # Build command based on operation type
        if self.name == "Create Fail Mode":
            return self._build_create_fail_mode_command(row_data)
        elif self.name == "Create Cause":
            return self._build_create_cause_command(row_data)
        else:
            raise OperationBuildError(f"Unknown operation: {self.name}")
    
    def _build_create_fail_mode_command(self, row_data: Dict[str, str]) -> str:
        """Build command for creating a fail mode."""
        # Quote description to handle special characters
        description = row_data.get("Description", "").replace('"', '\\"')
        function_id = row_data.get("Function ID", "")
        severity = row_data.get("Severity", "")
        
        return f'rvs create-failmode --function-id "{function_id}" --description "{description}" --severity "{severity}"'
    
    def _build_create_cause_command(self, row_data: Dict[str, str]) -> str:
        """Build command for creating a cause."""
        description = row_data.get("Description", "").replace('"', '\\"')
        fail_mode_id = row_data.get("Fail Mode ID", "")
        probability = row_data.get("Probability", "")
        
        return f'rvs create-cause --fail-mode-id "{fail_mode_id}" --description "{description}" --probability "{probability}"'


class OperationRegistry:
    """Registry for managing operation templates."""
    
    def __init__(self) -> None:
        self._templates: Dict[str, OperationTemplate] = {}
    
    def register(self, template: OperationTemplate) -> None:
        """Register an operation template."""
        self._templates[template.name] = template
    
    def by_name(self, name: str) -> Optional[OperationTemplate]:
        """Get template by operation name."""
        return self._templates.get(name)
    
    def by_sheet(self, sheet_name: str) -> List[OperationTemplate]:
        """Get all templates for a given sheet."""
        return [template for template in self._templates.values() if template.sheet == sheet_name]
    
    def all_templates(self) -> List[OperationTemplate]:
        """Get all registered templates."""
        return list(self._templates.values())


# Global registry instance
REGISTRY = OperationRegistry()


def initialize_registry() -> None:
    """Initialize the global registry with default operations."""
    # Register Create Fail Mode operation
    create_fail_mode = OperationTemplate(
        sheet="Create Fail Modes",
        name="Create Fail Mode",
        required_columns=["Function ID", "Description", "Severity"]
    )
    REGISTRY.register(create_fail_mode)
    
    # Register Create Cause operation
    create_cause = OperationTemplate(
        sheet="Create Causes",
        name="Create Cause", 
        required_columns=["Fail Mode ID", "Description", "Probability"]
    )
    REGISTRY.register(create_cause)


# Initialize registry on import
initialize_registry()