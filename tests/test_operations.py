"""Tests for operations parsing and command generation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from fmc_agent.mock_data import create_sample_workbook
from fmc_agent.operations import ChangeLogManager, CommandExecutor, OperationParser


class TestOperationParser:
    """Test cases for OperationParser class."""

    def test_parse_fail_modes(self):
        """Test parsing Create Fail Modes operations."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                # Should find at least some operations (excluding completed ones)
                assert len(operations) >= 1

                # Check operation structure
                op = operations[0]
                assert op.operation_type == "Create Fail Modes"
                assert op.sheet_name == "Create Fail Modes"
                assert "im createissue" in op.command
                assert "--type='Fail Mode'" in op.command
                assert op.row_index > 1  # Should be >1 since row 1 is header

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_parse_causes(self):
        """Test parsing Create Causes operations."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Causes"])

                assert len(operations) >= 1

                op = operations[0]
                assert op.operation_type == "Create Causes"
                assert "im createissue" in op.command
                assert "--type='Cause'" in op.command

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_parse_all_operations(self):
        """Test parsing all operation types."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations()  # Parse all

                # Should find operations from multiple sheets
                assert len(operations) >= 4  # At least one from each sheet

                # Check that we have different operation types
                op_types = {op.operation_type for op in operations}
                expected_types = {"Create Fail Modes", "Create Causes", "Create Controls", "Create Control Causes"}
                assert op_types == expected_types

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_skip_completed_rows(self):
        """Test that rows with completed status are skipped."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                # Check that completed rows are skipped
                # Sample data has one fail mode marked as "Completed"
                for op in operations:
                    completed_status = op.row_data.get("Agent Status", "").lower()
                    assert completed_status not in ["completed", "success", "done"]

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_command_formatting(self):
        """Test that commands are properly formatted."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1
                op = operations[0]

                # Check command structure
                assert op.command.startswith("im createissue")
                assert "--type='Fail Mode'" in op.command

                # Check that placeholders are replaced
                assert "{" not in op.command  # No unreplaced placeholders
                assert "}" not in op.command

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_missing_sheet(self):
        """Test parsing operations from missing sheet."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create minimal workbook without all sheets
                import pandas as pd
                df = pd.DataFrame({"test": ["data"]})
                df.to_excel(tmp_file.name, sheet_name="Test Sheet", index=False)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                # Should return empty list for missing sheet
                assert len(operations) == 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)


class TestCommandExecutor:
    """Test cases for CommandExecutor class."""

    def test_dry_run_execution(self):
        """Test command execution in dry-run mode."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1

                executor = CommandExecutor(dry_run=True)
                success, output, extracted_id = executor.execute_operation(operations[0])

                # Dry-run should always succeed
                assert success is True
                assert "[DRY-RUN]" in output
                assert extracted_id is not None
                assert extracted_id.startswith("SIM-")

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_dry_run_id_generation(self):
        """Test that dry-run generates consistent dummy IDs."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1

                executor = CommandExecutor(dry_run=True)

                # Execute same operation twice
                _, _, id1 = executor.execute_operation(operations[0])
                _, _, id2 = executor.execute_operation(operations[0])

                # IDs should be consistent for same operation
                assert id1 == id2
                assert id1.startswith("SIM-CreateFailModes-")

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    @patch("subprocess.run")
    def test_real_execution_success(self, mock_subprocess):
        """Test real command execution with successful result."""
        # Mock successful subprocess execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Command executed successfully. Generated ID: 12345"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1

                executor = CommandExecutor(dry_run=False)
                success, output, extracted_id = executor.execute_operation(operations[0])

                assert success is True
                assert "Command executed successfully" in output
                assert extracted_id == "12345"

                # Verify subprocess was called
                mock_subprocess.assert_called_once()

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    @patch("subprocess.run")
    def test_real_execution_failure(self, mock_subprocess):
        """Test real command execution with failure result."""
        # Mock failed subprocess execution
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed: Invalid parameters"
        mock_subprocess.return_value = mock_result

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1

                executor = CommandExecutor(dry_run=False)
                success, output, extracted_id = executor.execute_operation(operations[0])

                assert success is False
                assert "Command failed" in output
                assert extracted_id is None

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_id_extraction_patterns(self):
        """Test ID extraction from various output patterns."""
        executor = CommandExecutor(dry_run=False)

        # Test various ID patterns
        test_cases = [
            ("ID: 12345", "12345"),
            ("Created Issue ID 67890", "67890"),
            ("Issue 9999 created successfully", "9999"),
            ("Generated #54321", "54321"),
            ("Result: 11111 processed", "11111"),
            ("No ID in this output", None),
        ]

        for output, expected_id in test_cases:
            extracted_id = executor._extract_id_from_output(output)
            assert extracted_id == expected_id


class TestChangeLogManager:
    """Test cases for ChangeLogManager class."""

    def test_append_entry(self):
        """Test appending entries to Change Log."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1
                operation = operations[0]

                # Add entry to change log
                change_log = ChangeLogManager(Path(tmp_file.name))
                change_log.append_entry(operation, True, "Success output", "12345")

                # Verify entry was added
                entries = change_log.get_recent_entries(1)
                assert len(entries) == 1

                entry = entries[0]
                assert "Create Fail Modes" in entry["Operation"]
                assert entry["Status"] == "Success"
                assert "12345" in entry["Details"]
                assert "Success output" in entry["CLI Output"]

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_multiple_entries(self):
        """Test adding multiple Change Log entries."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations()

                change_log = ChangeLogManager(Path(tmp_file.name))

                # Add multiple entries
                for i, operation in enumerate(operations[:3]):  # Add 3 entries
                    change_log.append_entry(operation, True, f"Output {i}", f"ID-{i}")

                # Verify entries
                entries = change_log.get_recent_entries(5)
                assert len(entries) == 3

                # Entries should be in chronological order (most recent last)
                for i, entry in enumerate(entries):
                    assert f"ID-{i}" in entry["Details"]

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_output_truncation(self):
        """Test that long output is truncated in Change Log."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                create_sample_workbook(tmp_file.name)

                parser = OperationParser(Path(tmp_file.name))
                operations = parser.parse_operations(["Create Fail Modes"])

                assert len(operations) >= 1
                operation = operations[0]

                # Create very long output
                long_output = "A" * 3000  # 3000 characters

                change_log = ChangeLogManager(Path(tmp_file.name))
                change_log.append_entry(operation, True, long_output, "12345")

                # Verify output was truncated
                entries = change_log.get_recent_entries(1)
                assert len(entries) == 1

                cli_output = entries[0]["CLI Output"]
                assert len(cli_output) <= 2020  # 2000 + "... [truncated]"
                assert cli_output.endswith("... [truncated]")

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
