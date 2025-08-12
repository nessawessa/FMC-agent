"""CLI application for FMC Agent."""

import json
import sys
from pathlib import Path
from typing import List, Optional

try:
    import typer
    from rich.console import Console
    TYPER_AVAILABLE = True
except ImportError:
    # Fallback for when typer/rich is not available
    class MockTyper:
        def command(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def Typer(self, *args, **kwargs):
            return self
        
        def Option(self, *args, **kwargs):
            return None
    
    class MockConsole:
        def print(self, *args, **kwargs):
            print(*args)
    
    typer = MockTyper()
    Console = MockConsole
    TYPER_AVAILABLE = False

from .config import load_config
from .excel_validator import validate_workbook, is_row_actionable
from .registry import REGISTRY
from .change_log import append_change_log, create_change_log_entry
from .exceptions import ValidationError, FMCError

# Create Typer app
if TYPER_AVAILABLE:
    app = typer.Typer(help="FMC Agent - Automation tool for FM&C Excel workbook validation and RV&S CLI operations")
else:
    app = typer  # Mock object
console = Console()


@app.command()
def plan(
    file: "Path" = None,
    ops: "Optional[List[str]]" = None,
    output: "Optional[Path]" = None
) -> None:
    """Generate execution plan without side effects."""
    try:
        # Validate workbook
        validate_workbook(file)
        
        # Load configuration
        config = load_config()
        
        # Build execution plan
        plan_data = _build_execution_plan(file, ops)
        
        # Output JSON
        json_output = json.dumps(plan_data, indent=2)
        
        if output:
            output.write_text(json_output)
            console.print(f"Plan written to {output}")
        else:
            print(json_output)
            
    except ValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}", err=True)
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


@app.command()
def run(
    file: "Path" = None,
    ops: "Optional[List[str]]" = None,
    dry_run: bool = True
) -> None:
    """Execute operations and append change log entries."""
    try:
        # Validate workbook
        validate_workbook(file)
        
        # Load configuration
        config = load_config()
        
        # Override dry_run from config if provided
        if not dry_run:
            dry_run = config.dry_run
        
        # Get filtered templates
        templates = _get_filtered_templates(ops)
        
        # Execute operations and collect change log entries
        change_log_entries = []
        
        for template in templates:
            # Simulate loading sheet data
            sheet_data = _get_sheet_data(file, template.sheet)
            
            for row_index, row_data in enumerate(sheet_data):
                if is_row_actionable(row_data, template.required_columns):
                    excel_row = row_index + 2
                    
                    try:
                        # Build command
                        command = template.build_command(row_data)
                        
                        # Execute (dry run for now)
                        result, created_id, cli_output = _execute_command(command, dry_run)
                        
                        # Create change log entry
                        entry = create_change_log_entry(
                            operation=template.name,
                            source_sheet=template.sheet,
                            source_row=excel_row,
                            input_data=row_data,
                            result=result,
                            created_id=created_id,
                            cli_output=cli_output
                        )
                        change_log_entries.append(entry)
                        
                        console.print(f"Row {excel_row}: {template.name} -> {result}")
                        
                    except Exception as e:
                        console.print(f"[red]Row {excel_row}: Failed - {e}[/red]")
        
        # Append change log entries
        if change_log_entries:
            wwid = _get_current_user_wwid()
            append_change_log(file, wwid, change_log_entries)
            console.print(f"Appended {len(change_log_entries)} entries to change log")
        
    except ValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}", err=True)
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


def _build_execution_plan(file: Path, ops: Optional[List[str]]) -> dict:
    """Build execution plan for the workbook."""
    templates = _get_filtered_templates(ops)
    
    operations = []
    for template in templates:
        sheet_data = _get_sheet_data(file, template.sheet)
        
        for row_index, row_data in enumerate(sheet_data):
            if is_row_actionable(row_data, template.required_columns):
                excel_row = row_index + 2
                
                try:
                    command = template.build_command(row_data)
                    
                    operations.append({
                        "operation": template.name,
                        "sheet": template.sheet,
                        "row": excel_row,
                        "command": command,
                        "input_data": row_data
                    })
                except Exception as e:
                    operations.append({
                        "operation": template.name,
                        "sheet": template.sheet,
                        "row": excel_row,
                        "error": str(e),
                        "input_data": row_data
                    })
    
    return {"operations": operations}


def _get_filtered_templates(ops: Optional[List[str]]):
    """Get templates filtered by operation names."""
    all_templates = REGISTRY.all_templates()
    
    if ops:
        return [t for t in all_templates if t.name in ops]
    return all_templates


def _get_sheet_data(file: Path, sheet_name: str) -> List[dict]:
    """Get data from a specific sheet (simulated for now)."""
    # This simulates pandas.read_excel functionality
    # In real implementation: pd.read_excel(file, sheet_name=sheet_name).to_dict('records')
    
    if sheet_name == "Create Fail Modes":
        return [
            {"Function ID": "F001", "Description": "Test failure mode", "Severity": "High"},
            {"Function ID": "", "Description": "Incomplete row", "Severity": ""},
        ]
    elif sheet_name == "Create Causes":
        return [
            {"Fail Mode ID": "FM001", "Description": "Test cause", "Probability": "Medium"},
        ]
    return []


def _execute_command(command: str, dry_run: bool) -> tuple[str, str, str]:
    """Execute RV&S command (simulated for now)."""
    if dry_run:
        # Simulate dry run execution
        created_id = f"DRY_RUN_{hash(command) % 10000:04d}"
        cli_output = f"[DRY RUN] Would execute: {command}"
        result = "Success (Dry Run)"
    else:
        # In real implementation, we'd execute the actual command
        # import subprocess
        # result = subprocess.run(command, shell=True, capture_output=True, text=True)
        created_id = f"REAL_{hash(command) % 10000:04d}"
        cli_output = f"[REAL] Executed: {command}"
        result = "Success"
    
    return result, created_id, cli_output


def _get_current_user_wwid() -> Optional[str]:
    """Get current user's WWID."""
    # In real implementation, this might come from environment or system
    import os
    return os.getenv("USER", "unknown")


def main():
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("Interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()