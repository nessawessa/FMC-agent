"""Tests for Excel workbook validation functionality."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from fmc_agent.excel_validator import ExcelValidator
from fmc_agent.mock_data import create_sample_workbook
from fmc_agent.schemas import SHEET_SCHEMAS


class TestExcelValidator:
    """Test cases for ExcelValidator class."""

    def test_valid_workbook(self):
        """Test validation of a valid sample workbook."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create valid sample workbook
                create_sample_workbook(tmp_file.name)

                # Test validation
                validator = ExcelValidator(Path(tmp_file.name))
                is_valid, errors = validator.validate()

                assert is_valid is True
                assert len(errors) == 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_missing_file(self):
        """Test validation with non-existent file."""
        validator = ExcelValidator(Path("nonexistent.xlsx"))
        is_valid, errors = validator.validate()

        assert is_valid is False
        assert len(errors) > 0
        assert "Failed to load workbook" in errors[0]

    def test_missing_sheets(self):
        """Test validation with missing required sheets."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create workbook with only one sheet
                df = pd.DataFrame({"Column1": ["value1"], "Column2": ["value2"]})
                df.to_excel(tmp_file.name, sheet_name="Incomplete Sheet", index=False)

                # Test validation
                validator = ExcelValidator(Path(tmp_file.name))
                is_valid, errors = validator.validate()

                assert is_valid is False
                assert len(errors) > 0

                # Check that missing sheet errors are reported
                missing_sheet_errors = [e for e in errors if "Missing required sheet" in e]
                assert len(missing_sheet_errors) > 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_missing_columns(self):
        """Test validation with missing required columns."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create workbook with correct sheets but missing columns
                with pd.ExcelWriter(tmp_file.name, engine="openpyxl") as writer:
                    for sheet_name in SHEET_SCHEMAS.keys():
                        # Create sheet with only partial columns
                        partial_columns = SHEET_SCHEMAS[sheet_name][:2]  # Only first 2 columns
                        df = pd.DataFrame({col: ["test"] for col in partial_columns})
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Test validation
                validator = ExcelValidator(Path(tmp_file.name))
                is_valid, errors = validator.validate()

                assert is_valid is False
                assert len(errors) > 0

                # Check that missing column errors are reported
                missing_col_errors = [e for e in errors if "missing required column" in e]
                assert len(missing_col_errors) > 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_sheet_summary(self):
        """Test sheet summary functionality."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create valid sample workbook
                create_sample_workbook(tmp_file.name)

                # Get sheet summary
                validator = ExcelValidator(Path(tmp_file.name))
                summary = validator.get_sheet_summary()

                # Check summary structure
                assert isinstance(summary, dict)
                assert len(summary) == len(SHEET_SCHEMAS)

                # Check that all required sheets are reported
                for sheet_name in SHEET_SCHEMAS.keys():
                    assert sheet_name in summary
                    sheet_info = summary[sheet_name]
                    assert "status" in sheet_info
                    assert "rows" in sheet_info

                    # Valid sheets should have "present" status
                    if sheet_info["status"] == "present":
                        assert "columns" in sheet_info
                        assert sheet_info["rows"] >= 0
                        assert sheet_info["columns"] > 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_sheet_summary_with_missing_sheets(self):
        """Test sheet summary with some missing sheets."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create workbook with only some required sheets
                df = pd.DataFrame({"Column1": ["value1"], "Column2": ["value2"]})
                df.to_excel(tmp_file.name, sheet_name="Create Fail Modes", index=False)

                # Get sheet summary
                validator = ExcelValidator(Path(tmp_file.name))
                summary = validator.get_sheet_summary()

                # Check that present sheet is reported correctly
                assert summary["Create Fail Modes"]["status"] == "present"

                # Check that missing sheets are reported
                missing_sheets = [name for name, info in summary.items()
                                if info["status"] == "missing"]
                assert len(missing_sheets) > 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_validation_with_extra_sheets(self):
        """Test that extra sheets don't cause validation failure."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create valid sample workbook
                create_sample_workbook(tmp_file.name)

                # Add extra sheet
                with pd.ExcelWriter(tmp_file.name, mode="a", engine="openpyxl") as writer:
                    extra_df = pd.DataFrame({"Extra Column": ["extra data"]})
                    extra_df.to_excel(writer, sheet_name="Extra Sheet", index=False)

                # Test validation
                validator = ExcelValidator(Path(tmp_file.name))
                is_valid, errors = validator.validate()

                # Should still be valid - extra sheets are allowed
                assert is_valid is True
                assert len(errors) == 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_validation_with_extra_columns(self):
        """Test that extra columns don't cause validation failure."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Create sample data with extra columns
                with pd.ExcelWriter(tmp_file.name, engine="openpyxl") as writer:
                    for sheet_name, required_columns in SHEET_SCHEMAS.items():
                        # Add all required columns plus some extra ones
                        all_columns = required_columns + ["Extra Column 1", "Extra Column 2"]
                        df = pd.DataFrame({col: ["test"] for col in all_columns})
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Test validation
                validator = ExcelValidator(Path(tmp_file.name))
                is_valid, errors = validator.validate()

                # Should be valid - extra columns are allowed
                assert is_valid is True
                assert len(errors) == 0

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)

    def test_corrupted_excel_file(self):
        """Test handling of corrupted Excel files."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            try:
                # Write invalid Excel content
                tmp_file.write(b"This is not a valid Excel file")
                tmp_file.flush()

                # Test validation
                validator = ExcelValidator(Path(tmp_file.name))
                is_valid, errors = validator.validate()

                assert is_valid is False
                assert len(errors) > 0
                assert "Failed to load workbook" in errors[0]

            finally:
                Path(tmp_file.name).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
