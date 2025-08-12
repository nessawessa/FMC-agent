"""Basic CLI tests for FM&C Agent."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fmc_agent.cli import app
from fmc_agent.mock_data import create_sample_workbook

runner = CliRunner()


def test_cli_help():
    """Test that CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "FM&C Automation CLI" in result.stdout


def test_cli_version():
    """Test that CLI version command works."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "FM&C Agent v" in result.stdout


def test_validate_command_help():
    """Test validate command help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate an FM&C Modification Template workbook" in result.stdout


def test_run_command_help():
    """Test run command help."""
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "Execute operations from an FM&C Modification Template workbook" in result.stdout


def test_validate_missing_file():
    """Test validate command with non-existent file."""
    result = runner.invoke(app, ["validate", "--file", "nonexistent.xlsx"])
    assert result.exit_code != 0


def test_validate_sample_workbook():
    """Test validate command with sample workbook."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # Test validation
            result = runner.invoke(app, ["validate", "--file", tmp_file.name])
            assert result.exit_code == 0
            assert "Validation passed" in result.stdout

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


def test_validate_with_summary():
    """Test validate command with summary option."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # Test validation with summary
            result = runner.invoke(app, ["validate", "--file", tmp_file.name, "--summary"])
            assert result.exit_code == 0
            assert "Validation passed" in result.stdout
            assert "Sheet Summary" in result.stdout

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


def test_run_dry_run():
    """Test run command in dry-run mode."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # Test dry-run execution
            result = runner.invoke(app, [
                "run",
                "--file", tmp_file.name,
                "--dry-run",
                "--ops", "Create Fail Modes",
            ])

            # Should succeed in dry-run mode
            assert result.exit_code == 0
            assert "DRY-RUN MODE" in result.stdout
            assert "Execution Plan" in result.stdout

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


def test_run_multiple_operations():
    """Test run command with multiple operation types."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # Test with multiple operations
            result = runner.invoke(app, [
                "run",
                "--file", tmp_file.name,
                "--dry-run",
                "--ops", "Create Fail Modes",
                "--ops", "Create Causes",
            ])

            assert result.exit_code == 0
            assert "DRY-RUN MODE" in result.stdout

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


def test_changelog_command():
    """Test changelog command."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # First run some operations to create changelog entries
            runner.invoke(app, [
                "run",
                "--file", tmp_file.name,
                "--dry-run",
                "--ops", "Create Fail Modes",
            ])

            # Then test changelog command
            result = runner.invoke(app, ["changelog", "--file", tmp_file.name])

            # Should show recent entries or indicate no entries found
            assert result.exit_code == 0

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


def test_verbose_logging():
    """Test verbose logging option."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # Test with verbose flag
            result = runner.invoke(app, [
                "--verbose",
                "validate",
                "--file", tmp_file.name,
            ])

            assert result.exit_code == 0

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


def test_debug_logging():
    """Test debug logging option."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        try:
            # Create sample workbook
            create_sample_workbook(tmp_file.name)

            # Test with debug flag
            result = runner.invoke(app, [
                "--debug",
                "validate",
                "--file", tmp_file.name,
            ])

            assert result.exit_code == 0

        finally:
            Path(tmp_file.name).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
