"""Typer-based CLI for FM&C Automation Agent."""

import logging
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .excel_validator import ExcelValidator
from .logging_setup import setup_logging
from .operations import ChangeLogManager, CommandExecutor, OperationParser

# Create Typer app
app = typer.Typer(
    name="fmc",
    help="FM&C Automation CLI for validating and executing workbook operations",
    add_completion=False,
)

# Rich console for pretty output
console = Console()
logger = logging.getLogger(__name__)


def version_callback(value: bool):
    """Show version information."""
    if value:
        console.print(f"FM&C Agent v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback,
        help="Show version and exit",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Enable verbose logging",
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging",
    ),
):
    """FM&C Automation Agent CLI."""
    if debug:
        setup_logging("DEBUG")
    elif verbose:
        setup_logging("INFO")
    else:
        setup_logging("WARNING")


@app.command()
def validate(
    file: Path = typer.Option(
        ..., "--file", "-f", help="Path to FM&C Modification Template workbook",
        exists=True, file_okay=True, dir_okay=False, readable=True,
    ),
    summary: bool = typer.Option(
        False, "--summary", "-s", help="Show sheet summary information",
    ),
):
    """Validate an FM&C Modification Template workbook."""
    console.print(f"[bold blue]Validating workbook:[/bold blue] {file}")

    try:
        validator = ExcelValidator(file)
        is_valid, errors = validator.validate()

        if is_valid:
            console.print("[bold green]✓ Validation passed[/bold green]")
        else:
            console.print("[bold red]✗ Validation failed[/bold red]")
            console.print("\n[bold red]Errors found:[/bold red]")
            for error in errors:
                console.print(f"  • {error}")

        if summary:
            console.print("\n[bold blue]Sheet Summary:[/bold blue]")
            sheet_summary = validator.get_sheet_summary()

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Sheet Name")
            table.add_column("Status")
            table.add_column("Rows")
            table.add_column("Columns")

            for sheet_name, info in sheet_summary.items():
                status = info.get("status", "unknown")
                rows = str(info.get("rows", 0))
                columns = str(info.get("columns", 0)) if "columns" in info else "N/A"

                # Color code the status
                if status == "present":
                    status_colored = f"[green]{status}[/green]"
                elif status == "missing":
                    status_colored = f"[red]{status}[/red]"
                else:
                    status_colored = f"[yellow]{status}[/yellow]"

                table.add_row(sheet_name, status_colored, rows, columns)

            console.print(table)

        # Exit with error code if validation failed
        if not is_valid:
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]Error during validation: {e}[/bold red]")
        logger.exception("Validation error")
        raise typer.Exit(1)


@app.command()
def run(
    file: Path = typer.Option(
        ..., "--file", "-f", help="Path to FM&C Modification Template workbook",
        exists=True, file_okay=True, dir_okay=False, readable=True,
    ),
    ops: List[str] = typer.Option(
        None, "--ops", help="Operation types to execute (e.g., 'Create Fail Modes')",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate execution without running actual commands",
    ),
    validate_first: bool = typer.Option(
        True, "--validate/--no-validate", help="Validate workbook before execution",
    ),
):
    """Execute operations from an FM&C Modification Template workbook."""
    console.print(f"[bold blue]Processing workbook:[/bold blue] {file}")

    if dry_run:
        console.print("[bold yellow]DRY-RUN MODE: Commands will be simulated[/bold yellow]")

    try:
        # Validate workbook first if requested
        if validate_first:
            console.print("Validating workbook...")
            validator = ExcelValidator(file)
            is_valid, errors = validator.validate()

            if not is_valid:
                console.print("[bold red]Validation failed. Aborting execution.[/bold red]")
                for error in errors:
                    console.print(f"  • {error}")
                raise typer.Exit(1)
            console.print("[green]✓ Validation passed[/green]")

        # Parse operations
        parser = OperationParser(file)
        operations = parser.parse_operations(ops)

        if not operations:
            console.print("[yellow]No operations found to execute[/yellow]")
            return

        console.print(f"Found {len(operations)} operations to execute")

        # Show execution plan
        console.print("\n[bold blue]Execution Plan:[/bold blue]")
        for i, op in enumerate(operations, 1):
            console.print(f"  {i}. {op.operation_type} - Row {op.row_index}")

        if not dry_run:
            # Confirm execution in non-dry-run mode
            confirm = typer.confirm("Do you want to proceed with execution?")
            if not confirm:
                console.print("Execution cancelled")
                return

        # Execute operations
        executor = CommandExecutor(dry_run=dry_run)
        change_log = ChangeLogManager(file)

        success_count = 0
        failure_count = 0

        console.print(f"\n[bold blue]Executing {len(operations)} operations:[/bold blue]")

        for i, operation in enumerate(operations, 1):
            console.print(f"\n[{i}/{len(operations)}] {operation.operation_type} - Row {operation.row_index}")

            # Execute the operation
            success, output, extracted_id = executor.execute_operation(operation)

            # Update counters
            if success:
                success_count += 1
                console.print("[green]✓ Success[/green]")
                if extracted_id:
                    console.print(f"  Generated ID: {extracted_id}")
            else:
                failure_count += 1
                console.print("[red]✗ Failed[/red]")

            # Show truncated output
            if output:
                truncated_output = output[:200]
                if len(output) > 200:
                    truncated_output += "..."
                console.print(f"  Output: {truncated_output}")

            # Add to change log
            try:
                change_log.append_entry(operation, success, output, extracted_id)
            except Exception as e:
                logger.warning(f"Failed to update change log: {e}")

        # Show summary
        console.print("\n[bold blue]Execution Summary:[/bold blue]")
        console.print(f"  Total operations: {len(operations)}")
        console.print(f"  [green]Successful: {success_count}[/green]")
        console.print(f"  [red]Failed: {failure_count}[/red]")

        if failure_count > 0:
            console.print("\n[yellow]Some operations failed. Check the Change Log sheet for details.[/yellow]")
            raise typer.Exit(1)
        console.print("\n[green]All operations completed successfully![/green]")

    except Exception as e:
        console.print(f"[bold red]Error during execution: {e}[/bold red]")
        logger.exception("Execution error")
        raise typer.Exit(1)


@app.command()
def changelog(
    file: Path = typer.Option(
        ..., "--file", "-f", help="Path to FM&C Modification Template workbook",
        exists=True, file_okay=True, dir_okay=False, readable=True,
    ),
    count: int = typer.Option(
        10, "--count", "-n", help="Number of recent entries to show",
    ),
):
    """Show recent Change Log entries from a workbook."""
    console.print(f"[bold blue]Recent Change Log entries from:[/bold blue] {file}")

    try:
        change_log = ChangeLogManager(file)
        entries = change_log.get_recent_entries(count)

        if not entries:
            console.print("[yellow]No Change Log entries found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Timestamp", width=20)
        table.add_column("Operation", width=30)
        table.add_column("Status", width=10)
        table.add_column("Details", width=30)

        for entry in entries:
            timestamp = entry.get("Timestamp", "")
            operation = entry.get("Operation", "")
            status = entry.get("Status", "")
            details = entry.get("Details", "")

            # Color code the status
            if status.lower() == "success":
                status_colored = f"[green]{status}[/green]"
            else:
                status_colored = f"[red]{status}[/red]"

            table.add_row(timestamp, operation, status_colored, details)

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error reading Change Log: {e}[/bold red]")
        logger.exception("Change Log error")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
