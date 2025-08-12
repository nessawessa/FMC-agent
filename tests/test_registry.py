"""Tests for operation registry."""

import pytest
from fmc_agent.registry import OperationTemplate, OperationRegistry, REGISTRY, initialize_registry
from fmc_agent.exceptions import OperationBuildError


def test_operation_template_build_create_fail_mode():
    """Test building command for Create Fail Mode operation."""
    template = OperationTemplate(
        sheet="Create Fail Modes",
        name="Create Fail Mode",
        required_columns=["Function ID", "Description", "Severity"]
    )
    
    row_data = {
        "Function ID": "F001",
        "Description": "Test failure mode",
        "Severity": "High"
    }
    
    command = template.build_command(row_data)
    expected = 'rvs create-failmode --function-id "F001" --description "Test failure mode" --severity "High"'
    assert command == expected


def test_operation_template_build_create_cause():
    """Test building command for Create Cause operation."""
    template = OperationTemplate(
        sheet="Create Causes",
        name="Create Cause",
        required_columns=["Fail Mode ID", "Description", "Probability"]
    )
    
    row_data = {
        "Fail Mode ID": "FM001",
        "Description": "Test cause",
        "Probability": "Medium"
    }
    
    command = template.build_command(row_data)
    expected = 'rvs create-cause --fail-mode-id "FM001" --description "Test cause" --probability "Medium"'
    assert command == expected


def test_operation_template_build_missing_required_column():
    """Test that missing required column raises error."""
    template = OperationTemplate(
        sheet="Create Fail Modes", 
        name="Create Fail Mode",
        required_columns=["Function ID", "Description", "Severity"]
    )
    
    row_data = {
        "Function ID": "F001",
        "Description": "Test failure mode"
        # Missing "Severity"
    }
    
    with pytest.raises(OperationBuildError, match="Missing required column 'Severity'"):
        template.build_command(row_data)


def test_operation_template_build_unknown_operation():
    """Test that unknown operation raises error."""
    template = OperationTemplate(
        sheet="Unknown Sheet",
        name="Unknown Operation",
        required_columns=["Test"]
    )
    
    row_data = {"Test": "value"}
    
    with pytest.raises(OperationBuildError, match="Unknown operation: Unknown Operation"):
        template.build_command(row_data)


def test_operation_template_command_escapes_quotes():
    """Test that quotes in descriptions are properly escaped."""
    template = OperationTemplate(
        sheet="Create Fail Modes",
        name="Create Fail Mode", 
        required_columns=["Function ID", "Description", "Severity"]
    )
    
    row_data = {
        "Function ID": "F001",
        "Description": 'Test "quoted" description',
        "Severity": "High"
    }
    
    command = template.build_command(row_data)
    assert 'Test \\"quoted\\" description' in command


def test_operation_registry_register():
    """Test registering operation templates."""
    registry = OperationRegistry()
    
    template = OperationTemplate(
        sheet="Test Sheet",
        name="Test Operation",
        required_columns=["Test Column"]
    )
    
    registry.register(template)
    assert registry.by_name("Test Operation") == template


def test_operation_registry_by_name():
    """Test retrieving template by name."""
    registry = OperationRegistry()
    
    template = OperationTemplate(
        sheet="Test Sheet",
        name="Test Operation", 
        required_columns=["Test Column"]
    )
    
    registry.register(template)
    
    result = registry.by_name("Test Operation")
    assert result == template
    
    result = registry.by_name("Nonexistent")
    assert result is None


def test_operation_registry_by_sheet():
    """Test retrieving templates by sheet name."""
    registry = OperationRegistry()
    
    template1 = OperationTemplate(
        sheet="Test Sheet",
        name="Operation 1",
        required_columns=["Col1"]
    )
    
    template2 = OperationTemplate(
        sheet="Test Sheet", 
        name="Operation 2",
        required_columns=["Col2"]
    )
    
    template3 = OperationTemplate(
        sheet="Other Sheet",
        name="Operation 3",
        required_columns=["Col3"]
    )
    
    registry.register(template1)
    registry.register(template2)
    registry.register(template3)
    
    test_sheet_templates = registry.by_sheet("Test Sheet")
    assert len(test_sheet_templates) == 2
    assert template1 in test_sheet_templates
    assert template2 in test_sheet_templates
    
    other_sheet_templates = registry.by_sheet("Other Sheet")
    assert len(other_sheet_templates) == 1
    assert template3 in other_sheet_templates


def test_global_registry_initialization():
    """Test that global registry is properly initialized."""
    # The registry should be initialized on import
    assert REGISTRY.by_name("Create Fail Mode") is not None
    assert REGISTRY.by_name("Create Cause") is not None
    
    create_fail_mode = REGISTRY.by_name("Create Fail Mode")
    assert create_fail_mode.sheet == "Create Fail Modes"
    assert "Function ID" in create_fail_mode.required_columns
    
    create_cause = REGISTRY.by_name("Create Cause")
    assert create_cause.sheet == "Create Causes"
    assert "Fail Mode ID" in create_cause.required_columns