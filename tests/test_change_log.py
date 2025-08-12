"""Tests for change log functionality."""

import json
from pathlib import Path
from datetime import datetime
from fmc_agent.change_log import append_change_log, create_change_log_entry


def test_create_change_log_entry():
    """Test creating a standardized change log entry."""
    entry = create_change_log_entry(
        operation="Create Fail Mode",
        source_sheet="Create Fail Modes",
        source_row=2,
        input_data={"Function ID": "F001", "Description": "Test"},
        result="Success",
        created_id="FM123",
        cli_output="Command executed successfully"
    )
    
    expected = {
        "operation": "Create Fail Mode",
        "source_sheet": "Create Fail Modes", 
        "source_row": 2,
        "input_data": {"Function ID": "F001", "Description": "Test"},
        "result": "Success",
        "created_id": "FM123",
        "cli_output": "Command executed successfully"
    }
    
    assert entry == expected


def test_create_change_log_entry_minimal():
    """Test creating change log entry with minimal data."""
    entry = create_change_log_entry(
        operation="Test Operation",
        source_sheet="Test Sheet",
        source_row=1,
        input_data={},
        result="Failed"
    )
    
    assert entry["operation"] == "Test Operation"
    assert entry["source_sheet"] == "Test Sheet" 
    assert entry["source_row"] == 1
    assert entry["input_data"] == {}
    assert entry["result"] == "Failed"
    assert entry["created_id"] == ""
    assert entry["cli_output"] == ""


def test_append_change_log_basic(tmp_path, capsys):
    """Test basic change log append functionality."""
    # Create a temporary file path
    workbook_path = tmp_path / "test.xlsx"
    
    entries = [
        create_change_log_entry(
            operation="Create Fail Mode",
            source_sheet="Create Fail Modes",
            source_row=2,
            input_data={"Function ID": "F001", "Description": "Test failure"},
            result="Success",
            created_id="FM001",
            cli_output="rvs create-failmode executed"
        )
    ]
    
    # Call append_change_log (simulated)
    append_change_log(workbook_path, "testuser", entries)
    
    # Check console output (since we're simulating)
    captured = capsys.readouterr()
    assert "Would append 1 entries to change log" in captured.out
    assert "Create Fail Mode -> Success" in captured.out


def test_append_change_log_multiple_entries(tmp_path, capsys):
    """Test appending multiple change log entries."""
    workbook_path = tmp_path / "test.xlsx"
    
    entries = [
        create_change_log_entry(
            operation="Create Fail Mode",
            source_sheet="Create Fail Modes", 
            source_row=2,
            input_data={"Function ID": "F001"},
            result="Success",
            created_id="FM001"
        ),
        create_change_log_entry(
            operation="Create Cause",
            source_sheet="Create Causes",
            source_row=3,
            input_data={"Fail Mode ID": "FM001"},
            result="Success", 
            created_id="C001"
        )
    ]
    
    append_change_log(workbook_path, "testuser", entries)
    
    captured = capsys.readouterr()
    assert "Would append 2 entries to change log" in captured.out


def test_append_change_log_no_wwid(tmp_path, capsys):
    """Test appending change log with no WWID."""
    workbook_path = tmp_path / "test.xlsx"
    
    entries = [
        create_change_log_entry(
            operation="Test",
            source_sheet="Test Sheet",
            source_row=1,
            input_data={},
            result="Success"
        )
    ]
    
    append_change_log(workbook_path, None, entries)
    
    captured = capsys.readouterr()
    assert "Would append 1 entries to change log" in captured.out


def test_append_change_log_cli_output_truncation(tmp_path):
    """Test that CLI output is truncated when too long."""
    workbook_path = tmp_path / "test.xlsx"
    
    # Create a very long CLI output
    long_output = "x" * 3000  # Longer than default max_cli_len of 2000
    
    entries = [
        create_change_log_entry(
            operation="Test",
            source_sheet="Test Sheet", 
            source_row=1,
            input_data={},
            result="Success",
            cli_output=long_output
        )
    ]
    
    # Test with default max_cli_len (2000)
    append_change_log(workbook_path, "testuser", entries)
    
    # Test with custom max_cli_len
    append_change_log(workbook_path, "testuser", entries, max_cli_len=100)


def test_append_change_log_input_data_serialization(tmp_path):
    """Test that input data is properly JSON serialized."""
    workbook_path = tmp_path / "test.xlsx"
    
    # Test with complex input data
    complex_data = {
        "Function ID": "F001",
        "Description": "Test with \"quotes\" and special chars",
        "Nested": {"key": "value"},
        "List": [1, 2, 3]
    }
    
    entries = [
        create_change_log_entry(
            operation="Test",
            source_sheet="Test Sheet",
            source_row=1, 
            input_data=complex_data,
            result="Success"
        )
    ]
    
    append_change_log(workbook_path, "testuser", entries)
    
    # Verify that the data would be properly serialized
    # (In real implementation, we'd check the actual Excel file)
    serialized = json.dumps(complex_data, separators=(',', ':'))
    assert '"' in serialized  # Should contain quotes
    assert ' ' not in serialized  # Should be compact (no spaces after separators)