#!/usr/bin/env python3
"""
Legacy script: DataCheck.py
Reference implementation for data validation and consistency checks.

This is a reference script that demonstrates patterns used in the legacy system.
It is not imported or used by the new FM&C Agent but preserved for reference.
"""

import sys
import csv
import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class DataChecker:
    """Legacy data validation class."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)
        
    def check_csv_file(self, file_path: str, schema: Dict[str, List[str]]) -> bool:
        """Check CSV file against schema."""
        print(f"[LEGACY] DataCheck: Validating {file_path}")
        
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                
                # Check required columns
                required_cols = schema.get('required_columns', [])
                missing_cols = [col for col in required_cols if col not in fieldnames]
                if missing_cols:
                    self.errors.append(f"Missing required columns: {missing_cols}")
                    
                # Check data rows
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total_rows'] += 1
                    self._check_row(row, row_num, schema)
                    
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
            
        return len(self.errors) == 0
        
    def _check_row(self, row: Dict[str, str], row_num: int, 
                   schema: Dict[str, List[str]]) -> None:
        """Check individual row against schema."""
        # Check for empty required fields
        required_fields = schema.get('required_fields', [])
        for field in required_fields:
            if not row.get(field, '').strip():
                self.errors.append(f"Row {row_num}: Empty required field '{field}'")
                
        # Check ID format (legacy pattern)
        id_fields = schema.get('id_fields', [])
        for field in id_fields:
            value = row.get(field, '').strip()
            if value and not self._validate_id_format(value):
                self.warnings.append(f"Row {row_num}: Invalid ID format in '{field}': {value}")
                
    def _validate_id_format(self, id_value: str) -> bool:
        """Validate legacy ID format."""
        # Legacy ID pattern: XXXX-NNNN or similar
        if not id_value:
            return False
            
        # Basic validation - contains letters and numbers with hyphens
        import re
        pattern = r'^[A-Z]{1,4}-\d{3,6}$'
        return re.match(pattern, id_value) is not None
        
    def check_cross_references(self, fail_modes_file: str, causes_file: str) -> bool:
        """Check cross-references between fail modes and causes."""
        print("[LEGACY] DataCheck: Checking cross-references")
        
        # Load fail mode IDs
        fail_mode_ids = self._load_ids_from_csv(fail_modes_file, 'Fail_Mode_ID')
        
        # Check cause references
        try:
            with open(causes_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    fm_id = row.get('Fail_Mode_ID', '').strip()
                    if fm_id and fm_id not in fail_mode_ids:
                        self.errors.append(
                            f"Row {row_num} in {causes_file}: "
                            f"Invalid Fail Mode ID reference: {fm_id}"
                        )
        except Exception as e:
            self.errors.append(f"Error checking cross-references: {e}")
            return False
            
        return len(self.errors) == 0
        
    def _load_ids_from_csv(self, file_path: str, id_column: str) -> Set[str]:
        """Load IDs from CSV file."""
        ids = set()
        
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    id_value = row.get(id_column, '').strip()
                    if id_value:
                        ids.add(id_value)
        except Exception:
            pass  # Handle gracefully in legacy code
            
        return ids
        
    def check_duplicates(self, file_path: str, id_column: str) -> bool:
        """Check for duplicate IDs in file."""
        print(f"[LEGACY] DataCheck: Checking duplicates in {id_column}")
        
        seen_ids = set()
        duplicates = set()
        
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    id_value = row.get(id_column, '').strip()
                    if id_value:
                        if id_value in seen_ids:
                            duplicates.add(id_value)
                            self.errors.append(
                                f"Row {row_num}: Duplicate {id_column}: {id_value}"
                            )
                        else:
                            seen_ids.add(id_value)
        except Exception as e:
            self.errors.append(f"Error checking duplicates: {e}")
            return False
            
        self.stats['duplicate_ids'] = len(duplicates)
        return len(duplicates) == 0
        
    def generate_report(self) -> str:
        """Generate validation report."""
        report = {
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'statistics': dict(self.stats)
            },
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        return json.dumps(report, indent=2)


def load_schema(schema_file: str) -> Dict[str, List[str]]:
    """Load validation schema from JSON file."""
    try:
        with open(schema_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Schema file not found: {schema_file}")
        return {}
    except Exception as e:
        print(f"Error loading schema: {e}")
        return {}


def main():
    """Main entry point for legacy data checking script."""
    if len(sys.argv) < 3:
        print("Usage: DataCheck.py <data_file> <schema_file> [output_report]")
        print("  data_file: CSV file to validate")
        print("  schema_file: JSON schema definition")
        print("  output_report: Optional report output file")
        sys.exit(1)
        
    data_file = sys.argv[1]
    schema_file = sys.argv[2]
    report_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Load schema
    schema = load_schema(schema_file)
    if not schema:
        print("Error: Could not load validation schema")
        sys.exit(1)
        
    # Run validation
    checker = DataChecker()
    
    # Basic file validation
    valid = checker.check_csv_file(data_file, schema)
    
    # Check for duplicates if ID column specified
    if 'id_column' in schema:
        checker.check_duplicates(data_file, schema['id_column'])
        
    # Generate report
    report = checker.generate_report()
    
    if report_file:
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"[LEGACY] DataCheck: Report written to {report_file}")
    else:
        print(report)
        
    # Print summary
    print(f"[LEGACY] DataCheck: Validation completed")
    print(f"[LEGACY] DataCheck: Errors: {len(checker.errors)}")
    print(f"[LEGACY] DataCheck: Warnings: {len(checker.warnings)}")
    
    sys.exit(0 if len(checker.errors) == 0 else 1)


if __name__ == "__main__":
    main()