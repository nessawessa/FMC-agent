"""Sheet schema definitions for FM&C Modification Template workbook."""

from typing import Dict, List

# Mapping of sheet names to their required columns
SHEET_SCHEMAS: Dict[str, List[str]] = {
    "Create Fail Modes": [
        "Functional System ID",
        "Functional System Name",
        "Fail Mode ID",
        "Fail Mode Name",
        "Fail Mode Description",
        "Agent Status",
    ],
    "Create Causes": [
        "Fail Mode ID",
        "Cause ID",
        "Cause Name",
        "Cause Description",
        "Agent Status",
    ],
    "Create Controls": [
        "Cause ID",
        "Control ID",
        "Control Name",
        "Control Description",
        "Control Type",
        "Agent Status",
    ],
    "Create Control Causes": [
        "Control ID",
        "Cause ID",
        "Agent Status",
    ],
    "Change Log": [
        "Timestamp",
        "Operation",
        "Status",
        "Details",
        "CLI Output",
    ],
}

# Optional columns that may be present but are not required
OPTIONAL_COLUMNS: Dict[str, List[str]] = {
    "Create Fail Modes": [
        "Comments",
        "Priority",
        "Severity",
    ],
    "Create Causes": [
        "Comments",
        "Probability",
        "Impact",
    ],
    "Create Controls": [
        "Comments",
        "Effectiveness",
        "Implementation_Status",
    ],
    "Create Control Causes": [
        "Comments",
        "Relationship_Type",
    ],
}
