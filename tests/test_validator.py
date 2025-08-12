"""Tests for Excel validator."""

import pytest
from pathlib import Path
from fmc_agent.excel_validator import validate_workbook, is_row_actionable, _validate_sheet
from fmc_agent.exceptions import ValidationError


def test_is_row_actionable_with_content():
    """Test that row with any required column content is actionable."""
    row_data = {
        "Function ID": "F001",
        "Description": "",
        "Severity": ""
    }
    required_columns = ["Function ID", "Description", "Severity"]
    
    assert is_row_actionable(row_data, required_columns) is True


def test_is_row_actionable_without_content():
    """Test that row with no required column content is not actionable."""
    row_data = {
        "Function ID": "",
        "Description": "",
        "Severity": ""
    }
    required_columns = ["Function ID", "Description", "Severity"]
    
    assert is_row_actionable(row_data, required_columns) is False


def test_is_row_actionable_with_whitespace_only():
    """Test that row with only whitespace is not actionable."""
    row_data = {
        "Function ID": "   ",
        "Description": "\t",
        "Severity": "\n"
    }
    required_columns = ["Function ID", "Description", "Severity"]
    
    assert is_row_actionable(row_data, required_columns) is False


def test_validate_sheet_missing_columns():
    """Test validation of sheet with missing required columns."""
    sheet_data = [
        {"Function ID": "F001", "Description": "Test"}
        # Missing "Severity" column
    ]
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    assert len(issues) == 1
    assert "Missing required column 'Severity'" in issues[0]


def test_validate_sheet_partially_filled_row():
    """Test validation of sheet with partially filled actionable row."""
    sheet_data = [
        {
            "Function ID": "F001",
            "Description": "Test description",
            "Severity": ""  # Missing required data
        }
    ]
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    assert len(issues) == 1
    assert "Row 2" in issues[0]  # Excel row numbering
    assert "missing required data" in issues[0]
    assert "Severity" in issues[0]


def test_validate_sheet_multiple_missing_columns_in_row():
    """Test validation with multiple missing columns in actionable row."""
    sheet_data = [
        {
            "Function ID": "F001", 
            "Description": "",  # Missing
            "Severity": ""      # Missing
        }
    ]
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    assert len(issues) == 1
    assert "Description, Severity" in issues[0]


def test_validate_sheet_non_actionable_row_ignored():
    """Test that non-actionable rows are ignored."""
    sheet_data = [
        {
            "Function ID": "",
            "Description": "",
            "Severity": ""
        }
    ]
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    assert len(issues) == 0


def test_validate_sheet_success():
    """Test successful sheet validation."""
    sheet_data = [
        {
            "Function ID": "F001",
            "Description": "Test description",
            "Severity": "High"
        },
        {
            "Function ID": "",
            "Description": "",
            "Severity": ""  # Non-actionable row, should be ignored
        }
    ]
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    assert len(issues) == 0


def test_validate_sheet_empty_data():
    """Test validation of empty sheet data."""
    sheet_data = []
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    assert len(issues) == 0


def test_validate_workbook_missing_file():
    """Test validation of non-existent workbook file."""
    file_path = Path("/nonexistent/file.xlsx")
    
    with pytest.raises(ValidationError) as exc_info:
        validate_workbook(file_path)
    
    assert "Failed to read workbook" in str(exc_info.value)


def test_validate_workbook_success():
    """Test successful workbook validation (simulated)."""
    # This test uses the simulated workbook data
    file_path = Path("test.xlsx")
    
    # Should raise ValidationError due to incomplete row in simulated data
    with pytest.raises(ValidationError) as exc_info:
        validate_workbook(file_path)
    
    # Check that the validation caught the incomplete row
    issues = exc_info.value.issues
    assert any("Actionable row missing required data" in issue for issue in issues)


def test_excel_row_numbering():
    """Test that Excel row numbers are correct (start from 2 for data rows)."""
    sheet_data = [
        {"Function ID": "F001", "Description": "", "Severity": ""},  # Row 2 in Excel
        {"Function ID": "F002", "Description": "", "Severity": ""},  # Row 3 in Excel
    ]
    required_columns = ["Function ID", "Description", "Severity"]
    
    issues = _validate_sheet("Test Sheet", sheet_data, required_columns)
    
    # Should have issues for both rows
    assert len(issues) == 2
    assert "Row 2" in issues[0]
    assert "Row 3" in issues[1]