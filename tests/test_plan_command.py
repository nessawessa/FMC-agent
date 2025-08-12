"""Tests for plan command CLI functionality."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# For testing CLI without typer dependency
try:
    from typer.testing import CliRunner
    from fmc_agent.cli import app
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    CliRunner = None


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="Typer not available")
def test_plan_command_basic(tmp_path):
    """Test basic plan command functionality."""
    runner = CliRunner()
    
    # Create a test file
    test_file = tmp_path / "test.xlsx"
    test_file.touch()
    
    # Mock validation to pass
    with patch('fmc_agent.cli.validate_workbook'), \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        # Mock sheet data
        mock_get_sheet.side_effect = [
            [{"Function ID": "F001", "Description": "Test", "Severity": "High"}],  # Create Fail Modes
            [{"Fail Mode ID": "FM001", "Description": "Test cause", "Probability": "Medium"}]  # Create Causes
        ]
        
        result = runner.invoke(app, ["plan", "--file", str(test_file)])
        
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        assert "operations" in output_data
        assert len(output_data["operations"]) > 0


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="Typer not available")
def test_plan_command_with_output_file(tmp_path):
    """Test plan command with output file."""
    runner = CliRunner()
    
    test_file = tmp_path / "test.xlsx"
    test_file.touch()
    
    output_file = tmp_path / "plan.json"
    
    with patch('fmc_agent.cli.validate_workbook'), \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        mock_get_sheet.side_effect = [
            [{"Function ID": "F001", "Description": "Test", "Severity": "High"}],
            []
        ]
        
        result = runner.invoke(app, [
            "plan", 
            "--file", str(test_file),
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Check file content
        plan_data = json.loads(output_file.read_text())
        assert "operations" in plan_data


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="Typer not available")
def test_plan_command_with_ops_filter(tmp_path):
    """Test plan command with operation filter."""
    runner = CliRunner()
    
    test_file = tmp_path / "test.xlsx"
    test_file.touch()
    
    with patch('fmc_agent.cli.validate_workbook'), \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        mock_get_sheet.side_effect = [
            [{"Function ID": "F001", "Description": "Test", "Severity": "High"}],
        ]
        
        result = runner.invoke(app, [
            "plan",
            "--file", str(test_file),
            "--ops", "Create Fail Mode"
        ])
        
        assert result.exit_code == 0
        
        output_data = json.loads(result.stdout)
        operations = output_data["operations"]
        
        # Should only have Create Fail Mode operations
        for op in operations:
            assert op["operation"] == "Create Fail Mode"


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="Typer not available") 
def test_plan_command_validation_error(tmp_path):
    """Test plan command with validation error."""
    runner = CliRunner()
    
    test_file = tmp_path / "test.xlsx"
    test_file.touch()
    
    # Mock validation to fail
    with patch('fmc_agent.cli.validate_workbook') as mock_validate:
        from fmc_agent.exceptions import ValidationError
        mock_validate.side_effect = ValidationError(["Test validation error"])
        
        result = runner.invoke(app, ["plan", "--file", str(test_file)])
        
        assert result.exit_code == 2
        assert "Validation Error" in result.stderr


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="Typer not available")
def test_plan_command_missing_file():
    """Test plan command with missing file."""
    runner = CliRunner()
    
    result = runner.invoke(app, ["plan", "--file", "/nonexistent/file.xlsx"])
    
    assert result.exit_code == 1


def test_build_execution_plan():
    """Test building execution plan structure."""
    from fmc_agent.cli import _build_execution_plan
    
    test_file = Path("test.xlsx")
    
    with patch('fmc_agent.cli._get_filtered_templates') as mock_templates, \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        # Mock template
        mock_template = MagicMock()
        mock_template.name = "Create Fail Mode"
        mock_template.sheet = "Create Fail Modes"
        mock_template.required_columns = ["Function ID", "Description", "Severity"]
        mock_template.build_command.return_value = "test command"
        
        mock_templates.return_value = [mock_template]
        mock_get_sheet.return_value = [
            {"Function ID": "F001", "Description": "Test", "Severity": "High"}
        ]
        
        plan = _build_execution_plan(test_file, None)
        
        assert "operations" in plan
        assert len(plan["operations"]) == 1
        
        operation = plan["operations"][0]
        assert operation["operation"] == "Create Fail Mode"
        assert operation["sheet"] == "Create Fail Modes"
        assert operation["row"] == 2  # Excel row numbering
        assert operation["command"] == "test command"
        assert "input_data" in operation


def test_build_execution_plan_with_error():
    """Test building execution plan when command building fails."""
    from fmc_agent.cli import _build_execution_plan
    
    test_file = Path("test.xlsx")
    
    with patch('fmc_agent.cli._get_filtered_templates') as mock_templates, \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        # Mock template that raises error
        mock_template = MagicMock()
        mock_template.name = "Create Fail Mode"
        mock_template.sheet = "Create Fail Modes"
        mock_template.required_columns = ["Function ID", "Description", "Severity"]
        mock_template.build_command.side_effect = Exception("Test error")
        
        mock_templates.return_value = [mock_template]
        mock_get_sheet.return_value = [
            {"Function ID": "F001", "Description": "Test", "Severity": "High"}
        ]
        
        plan = _build_execution_plan(test_file, None)
        
        assert "operations" in plan
        assert len(plan["operations"]) == 1
        
        operation = plan["operations"][0]
        assert operation["operation"] == "Create Fail Mode"
        assert "error" in operation
        assert operation["error"] == "Test error"


def test_get_filtered_templates():
    """Test filtering templates by operation names."""
    from fmc_agent.cli import _get_filtered_templates
    
    # Test with no filter (should return all)
    templates = _get_filtered_templates(None)
    assert len(templates) >= 2  # Should have at least Create Fail Mode and Create Cause
    
    # Test with filter
    templates = _get_filtered_templates(["Create Fail Mode"])
    assert len(templates) == 1
    assert templates[0].name == "Create Fail Mode"
    
    # Test with multiple filters
    templates = _get_filtered_templates(["Create Fail Mode", "Create Cause"])
    assert len(templates) == 2
    
    # Test with non-existent operation
    templates = _get_filtered_templates(["Nonexistent Operation"])
    assert len(templates) == 0


def test_plan_json_structure_deterministic():
    """Test that plan JSON structure is deterministic."""
    from fmc_agent.cli import _build_execution_plan
    
    test_file = Path("test.xlsx")
    
    with patch('fmc_agent.cli._get_filtered_templates') as mock_templates, \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        # Create consistent mock data
        mock_template1 = MagicMock()
        mock_template1.name = "Create Fail Mode"
        mock_template1.sheet = "Create Fail Modes"
        mock_template1.required_columns = ["Function ID"]
        mock_template1.build_command.return_value = "command1"
        
        mock_template2 = MagicMock()
        mock_template2.name = "Create Cause"
        mock_template2.sheet = "Create Causes"
        mock_template2.required_columns = ["Fail Mode ID"]
        mock_template2.build_command.return_value = "command2"
        
        mock_templates.return_value = [mock_template1, mock_template2]
        mock_get_sheet.side_effect = [
            [{"Function ID": "F001"}],  # Create Fail Modes
            [{"Fail Mode ID": "FM001"}]  # Create Causes
        ]
        
        # Generate plan multiple times
        plan1 = _build_execution_plan(test_file, None)
        plan2 = _build_execution_plan(test_file, None)
        
        # Should be identical
        assert plan1 == plan2


def test_plan_command_json_output_valid():
    """Test that plan command outputs valid JSON."""
    from fmc_agent.cli import _build_execution_plan
    
    test_file = Path("test.xlsx")
    
    with patch('fmc_agent.cli._get_filtered_templates') as mock_templates, \
         patch('fmc_agent.cli._get_sheet_data') as mock_get_sheet:
        
        mock_template = MagicMock()
        mock_template.name = "Create Fail Mode"
        mock_template.sheet = "Create Fail Modes"
        mock_template.required_columns = ["Function ID"]
        mock_template.build_command.return_value = "test command"
        
        mock_templates.return_value = [mock_template]
        mock_get_sheet.return_value = [
            {"Function ID": "F001"}
        ]
        
        plan = _build_execution_plan(test_file, None)
        
        # Should be serializable to JSON
        json_str = json.dumps(plan, indent=2)
        
        # Should be parseable back
        parsed = json.loads(json_str)
        assert parsed == plan