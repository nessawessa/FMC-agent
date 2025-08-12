"""Sample data for testing and examples."""

from typing import Dict, List

import pandas as pd


def get_sample_fail_modes() -> List[Dict[str, str]]:
    """Get sample fail mode data for testing.
    
    Returns:
        List of dictionaries representing fail mode rows.
    """
    return [
        {
            "Functional System ID": "FS-001",
            "Functional System Name": "Engine Control System",
            "Fail Mode ID": "FM-001",
            "Fail Mode Name": "Engine Overheat",
            "Fail Mode Description": "Engine temperature exceeds safe operating limits",
            "Agent Status": "",
        },
        {
            "Functional System ID": "FS-001",
            "Functional System Name": "Engine Control System",
            "Fail Mode ID": "FM-002",
            "Fail Mode Name": "Engine Underspeed",
            "Fail Mode Description": "Engine fails to maintain minimum required RPM",
            "Agent Status": "",
        },
        {
            "Functional System ID": "FS-002",
            "Functional System Name": "Fuel System",
            "Fail Mode ID": "FM-003",
            "Fail Mode Name": "Fuel Leak",
            "Fail Mode Description": "Fuel escapes from intended containment",
            "Agent Status": "Completed",
        },
    ]


def get_sample_causes() -> List[Dict[str, str]]:
    """Get sample cause data for testing.
    
    Returns:
        List of dictionaries representing cause rows.
    """
    return [
        {
            "Fail Mode ID": "FM-001",
            "Cause ID": "C-001",
            "Cause Name": "Coolant Pump Failure",
            "Cause Description": "Primary coolant pump stops functioning",
            "Agent Status": "",
        },
        {
            "Fail Mode ID": "FM-001",
            "Cause ID": "C-002",
            "Cause Name": "Radiator Blockage",
            "Cause Description": "Coolant flow restricted through radiator",
            "Agent Status": "",
        },
        {
            "Fail Mode ID": "FM-002",
            "Cause ID": "C-003",
            "Cause Name": "Fuel Supply Restriction",
            "Cause Description": "Insufficient fuel delivery to engine",
            "Agent Status": "",
        },
    ]


def get_sample_controls() -> List[Dict[str, str]]:
    """Get sample control data for testing.
    
    Returns:
        List of dictionaries representing control rows.
    """
    return [
        {
            "Cause ID": "C-001",
            "Control ID": "CT-001",
            "Control Name": "Coolant Pump Monitoring",
            "Control Description": "Continuous monitoring of coolant pump operation",
            "Control Type": "Detection",
            "Agent Status": "",
        },
        {
            "Cause ID": "C-002",
            "Control ID": "CT-002",
            "Control Name": "Radiator Inspection",
            "Control Description": "Regular visual inspection of radiator for blockages",
            "Control Type": "Prevention",
            "Agent Status": "",
        },
        {
            "Cause ID": "C-003",
            "Control ID": "CT-003",
            "Control Name": "Fuel Flow Sensor",
            "Control Description": "Sensor to monitor fuel flow rate",
            "Control Type": "Detection",
            "Agent Status": "",
        },
    ]


def get_sample_control_causes() -> List[Dict[str, str]]:
    """Get sample control-cause relationship data for testing.
    
    Returns:
        List of dictionaries representing control-cause relationship rows.
    """
    return [
        {
            "Control ID": "CT-001",
            "Cause ID": "C-001",
            "Agent Status": "",
        },
        {
            "Control ID": "CT-002",
            "Cause ID": "C-002",
            "Agent Status": "",
        },
        {
            "Control ID": "CT-003",
            "Cause ID": "C-003",
            "Agent Status": "",
        },
    ]


def create_sample_workbook(file_path: str) -> None:
    """Create a sample workbook with test data.
    
    Args:
        file_path: Path where to save the sample workbook.
    """
    # Create DataFrames from sample data
    fail_modes_df = pd.DataFrame(get_sample_fail_modes())
    causes_df = pd.DataFrame(get_sample_causes())
    controls_df = pd.DataFrame(get_sample_controls())
    control_causes_df = pd.DataFrame(get_sample_control_causes())

    # Create Change Log with headers only
    change_log_df = pd.DataFrame(columns=[
        "Timestamp", "Operation", "Status", "Details", "CLI Output",
    ])

    # Write to Excel file with multiple sheets
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        fail_modes_df.to_excel(writer, sheet_name="Create Fail Modes", index=False)
        causes_df.to_excel(writer, sheet_name="Create Causes", index=False)
        controls_df.to_excel(writer, sheet_name="Create Controls", index=False)
        control_causes_df.to_excel(writer, sheet_name="Create Control Causes", index=False)
        change_log_df.to_excel(writer, sheet_name="Change Log", index=False)


def get_sample_sheet_data(sheet_name: str) -> List[Dict[str, str]]:
    """Get sample data for a specific sheet.
    
    Args:
        sheet_name: Name of the sheet to get sample data for.
        
    Returns:
        List of dictionaries representing rows for the specified sheet.
        
    Raises:
        ValueError: If sheet_name is not recognized.
    """
    sample_data_map = {
        "Create Fail Modes": get_sample_fail_modes,
        "Create Causes": get_sample_causes,
        "Create Controls": get_sample_controls,
        "Create Control Causes": get_sample_control_causes,
    }

    if sheet_name not in sample_data_map:
        raise ValueError(f"Unknown sheet name: {sheet_name}")

    return sample_data_map[sheet_name]()
