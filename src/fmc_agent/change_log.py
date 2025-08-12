"""Change log management for FMC Agent."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def append_change_log(
    path: Path, 
    wwid: Optional[str], 
    entries: List[Dict], 
    max_cli_len: int = 2000
) -> None:
    """Append change log entries to the workbook.
    
    Args:
        path: Path to the Excel workbook
        wwid: User's WWID (Windows ID)
        entries: List of change log entry dictionaries
        max_cli_len: Maximum length for CLI output truncation
    """
    # For now, simulate openpyxl functionality
    # In real implementation:
    # from openpyxl import load_workbook
    # workbook = load_workbook(path)
    
    # Simulate change log creation
    _simulate_change_log_append(path, wwid, entries, max_cli_len)


def _simulate_change_log_append(
    path: Path, 
    wwid: Optional[str], 
    entries: List[Dict], 
    max_cli_len: int
) -> None:
    """Simulate appending to change log (placeholder for real implementation)."""
    
    # Standard headers for change log
    headers = [
        "Timestamp",
        "WWID", 
        "Operation",
        "Source Sheet",
        "Source Row", 
        "Input Data",
        "Result",
        "Created ID",
        "CLI Output"
    ]
    
    # Process each entry
    processed_entries = []
    for entry in entries:
        timestamp = datetime.now().isoformat()
        
        # JSON-serialize Input Data compactly
        input_data = json.dumps(
            entry.get("input_data", {}), 
            separators=(',', ':')
        )
        
        # Truncate CLI output if too long
        cli_output = entry.get("cli_output", "")
        if len(cli_output) > max_cli_len:
            cli_output = cli_output[:max_cli_len] + "...[truncated]"
        
        processed_entry = {
            "Timestamp": timestamp,
            "WWID": wwid or "",
            "Operation": entry.get("operation", ""),
            "Source Sheet": entry.get("source_sheet", ""),
            "Source Row": entry.get("source_row", ""),
            "Input Data": input_data,
            "Result": entry.get("result", ""),
            "Created ID": entry.get("created_id", ""),
            "CLI Output": cli_output
        }
        processed_entries.append(processed_entry)
    
    # In real implementation, we would:
    # 1. Load the workbook
    # 2. Create "Change Log" sheet if it doesn't exist
    # 3. Add headers if this is a new sheet
    # 4. Append the processed entries as new rows
    # 5. Save the workbook
    
    print(f"Would append {len(processed_entries)} entries to change log in {path}")
    for entry in processed_entries:
        print(f"  {entry['Timestamp']}: {entry['Operation']} -> {entry['Result']}")


def create_change_log_entry(
    operation: str,
    source_sheet: str, 
    source_row: int,
    input_data: Dict,
    result: str,
    created_id: str = "",
    cli_output: str = ""
) -> Dict:
    """Create a standardized change log entry."""
    return {
        "operation": operation,
        "source_sheet": source_sheet,
        "source_row": source_row,
        "input_data": input_data,
        "result": result,
        "created_id": created_id,
        "cli_output": cli_output
    }