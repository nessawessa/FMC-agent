#!/usr/bin/env python3
"""
Legacy script: RemoveCCs.py
Reference implementation for removing Control-Cause relationships.

This is a reference script that demonstrates patterns used in the legacy system.
It is not imported or used by the new FM&C Agent but preserved for reference.
"""

import sys
import csv
from typing import List, Dict, Tuple

def remove_control_causes(input_file: str, output_file: str, 
                         remove_list: List[str]) -> Tuple[int, int]:
    """
    Remove specified Control-Cause relationships from data file.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        remove_list: List of Control-Cause IDs to remove
        
    Returns:
        Tuple of (total_processed, removed_count)
    """
    total_processed = 0
    removed_count = 0
    
    try:
        with open(input_file, 'r', newline='') as infile, \
             open(output_file, 'w', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for row in reader:
                total_processed += 1
                
                # Check if this Control-Cause relationship should be removed
                cc_id = f"{row.get('Control_ID', '')}-{row.get('Cause_ID', '')}"
                
                if cc_id in remove_list:
                    removed_count += 1
                    print(f"[LEGACY] Removing Control-Cause: {cc_id}")
                    continue  # Skip this row (remove it)
                    
                writer.writerow(row)
                
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
        return 0, 0
    except Exception as e:
        print(f"Error processing files: {e}")
        return 0, 0
        
    return total_processed, removed_count


def load_remove_list(remove_file: str) -> List[str]:
    """Load list of Control-Cause IDs to remove from file."""
    remove_list = []
    
    try:
        with open(remove_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    remove_list.append(line)
    except FileNotFoundError:
        print(f"Warning: Remove list file not found: {remove_file}")
    except Exception as e:
        print(f"Error reading remove list: {e}")
        
    return remove_list


def validate_csv_structure(csv_file: str) -> bool:
    """Validate that CSV has required columns."""
    required_columns = ['Control_ID', 'Cause_ID']
    
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            missing_columns = [col for col in required_columns if col not in fieldnames]
            if missing_columns:
                print(f"Error: Missing required columns: {missing_columns}")
                return False
                
    except Exception as e:
        print(f"Error validating CSV structure: {e}")
        return False
        
    return True


def main():
    """Main entry point for legacy Control-Cause removal script."""
    if len(sys.argv) < 4:
        print("Usage: RemoveCCs.py <input_csv> <output_csv> <remove_list_file>")
        print("  input_csv: CSV file with Control-Cause relationships")
        print("  output_csv: Output CSV file with relationships removed")
        print("  remove_list_file: Text file with Control-Cause IDs to remove")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    remove_file = sys.argv[3]
    
    # Validate input file structure
    if not validate_csv_structure(input_file):
        sys.exit(1)
        
    # Load removal list
    remove_list = load_remove_list(remove_file)
    if not remove_list:
        print("Warning: No items to remove found in remove list")
        
    print(f"[LEGACY] RemoveCCs: Processing {input_file}")
    print(f"[LEGACY] RemoveCCs: Will remove {len(remove_list)} relationships")
    
    # Process the file
    total, removed = remove_control_causes(input_file, output_file, remove_list)
    
    print(f"[LEGACY] RemoveCCs: Processed {total} relationships")
    print(f"[LEGACY] RemoveCCs: Removed {removed} relationships")
    print(f"[LEGACY] RemoveCCs: Output written to {output_file}")


if __name__ == "__main__":
    main()