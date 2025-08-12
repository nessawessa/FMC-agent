"""Excel workbook validator with row-level enforcement."""

from typing import Dict, List, Set
from pathlib import Path

from .exceptions import ValidationError
from .registry import REGISTRY


def validate_workbook(file_path: Path) -> None:
    """Validate workbook structure and data with strict row-level enforcement.
    
    Args:
        file_path: Path to the Excel workbook
        
    Raises:
        ValidationError: If validation fails with aggregated issues
    """
    issues = []
    
    try:
        # For now, simulate pandas/openpyxl functionality
        # In a real implementation, we'd use:
        # import pandas as pd
        # workbook_data = pd.read_excel(file_path, sheet_name=None)
        
        # Simulate workbook structure for testing
        workbook_data = _simulate_workbook_data(file_path)
        
        # Get all required sheets from registry
        required_sheets = set()
        for template in REGISTRY.all_templates():
            required_sheets.add(template.sheet)
        
        # Check for missing sheets
        available_sheets = set(workbook_data.keys())
        missing_sheets = required_sheets - available_sheets
        for sheet in missing_sheets:
            issues.append(f"Missing required sheet: '{sheet}'")
        
        # Validate each sheet
        for template in REGISTRY.all_templates():
            if template.sheet in workbook_data:
                sheet_issues = _validate_sheet(template.sheet, workbook_data[template.sheet], template.required_columns)
                issues.extend(sheet_issues)
        
        if issues:
            raise ValidationError(issues)
            
    except ValidationError:
        raise
    except Exception as e:
        issues.append(f"Failed to read workbook: {str(e)}")
        raise ValidationError(issues)


def _simulate_workbook_data(file_path: Path) -> Dict[str, List[Dict[str, str]]]:
    """Simulate workbook data for testing purposes."""
    # This is a placeholder - in real implementation we'd use pandas/openpyxl
    return {
        "Create Fail Modes": [
            {"Function ID": "F001", "Description": "Test failure mode", "Severity": "High"},
            {"Function ID": "", "Description": "Incomplete row", "Severity": ""},  # Invalid
        ],
        "Create Causes": [
            {"Fail Mode ID": "FM001", "Description": "Test cause", "Probability": "Medium"},
        ]
    }


def _validate_sheet(sheet_name: str, sheet_data: List[Dict[str, str]], required_columns: List[str]) -> List[str]:
    """Validate a single sheet for column presence and row-level data."""
    issues = []
    
    if not sheet_data:
        return issues
    
    # Check for missing required columns
    if sheet_data:
        available_columns = set(sheet_data[0].keys())
        missing_columns = set(required_columns) - available_columns
        for col in missing_columns:
            issues.append(f"Sheet '{sheet_name}': Missing required column '{col}'")
    
    # Validate row-level data
    for row_index, row in enumerate(sheet_data):
        excel_row = row_index + 2  # Excel row numbering (header is row 1)
        
        # Check if row is actionable (any required column has content)
        has_content = any(row.get(col, "").strip() for col in required_columns)
        
        if has_content:
            # If actionable, ALL required columns must be populated
            missing_in_row = []
            for col in required_columns:
                if not row.get(col, "").strip():
                    missing_in_row.append(col)
            
            if missing_in_row:
                issues.append(
                    f"Sheet '{sheet_name}', Row {excel_row}: "
                    f"Actionable row missing required data in columns: {', '.join(missing_in_row)}"
                )
    
    return issues


def is_row_actionable(row_data: Dict[str, str], required_columns: List[str]) -> bool:
    """Determine if a row is actionable (has any required column content)."""
    return any(row_data.get(col, "").strip() for col in required_columns)