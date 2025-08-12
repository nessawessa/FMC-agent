#!/usr/bin/env python3
"""
Legacy script: ExportCCs.py
Reference implementation for exporting Control-Cause relationships.

This is a reference script that demonstrates patterns used in the legacy system.
It is not imported or used by the new FM&C Agent but preserved for reference.
"""

import sys
import csv
import json
from typing import Dict, List, Optional
from datetime import datetime

def export_control_causes_csv(input_file: str, output_file: str, 
                             filter_criteria: Optional[Dict[str, str]] = None) -> int:
    """
    Export Control-Cause relationships to CSV format.
    
    Args:
        input_file: Path to input data file
        output_file: Path to output CSV file
        filter_criteria: Optional filtering criteria
        
    Returns:
        Number of relationships exported
    """
    exported_count = 0
    
    try:
        with open(input_file, 'r', newline='') as infile, \
             open(output_file, 'w', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            
            # Define output columns
            output_columns = [
                'Control_ID', 'Control_Name', 'Control_Type',
                'Cause_ID', 'Cause_Name', 'Relationship_Type',
                'Export_Date', 'Status'
            ]
            
            writer = csv.DictWriter(outfile, fieldnames=output_columns)
            writer.writeheader()
            
            for row in reader:
                # Apply filters if specified
                if filter_criteria and not _matches_criteria(row, filter_criteria):
                    continue
                    
                # Create export row
                export_row = {
                    'Control_ID': row.get('Control_ID', ''),
                    'Control_Name': row.get('Control_Name', ''),
                    'Control_Type': row.get('Control_Type', ''),
                    'Cause_ID': row.get('Cause_ID', ''),
                    'Cause_Name': row.get('Cause_Name', ''),
                    'Relationship_Type': row.get('Relationship_Type', 'Standard'),
                    'Export_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': 'Active'
                }
                
                writer.writerow(export_row)
                exported_count += 1
                
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
        return 0
    except Exception as e:
        print(f"Error during export: {e}")
        return 0
        
    return exported_count


def export_control_causes_json(input_file: str, output_file: str) -> int:
    """
    Export Control-Cause relationships to JSON format.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output JSON file
        
    Returns:
        Number of relationships exported
    """
    relationships = []
    
    try:
        with open(input_file, 'r', newline='') as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                relationship = {
                    'control': {
                        'id': row.get('Control_ID', ''),
                        'name': row.get('Control_Name', ''),
                        'type': row.get('Control_Type', '')
                    },
                    'cause': {
                        'id': row.get('Cause_ID', ''),
                        'name': row.get('Cause_Name', '')
                    },
                    'relationship_type': row.get('Relationship_Type', 'Standard'),
                    'export_metadata': {
                        'export_date': datetime.now().isoformat(),
                        'export_tool': 'ExportCCs.py (Legacy)',
                        'status': 'Active'
                    }
                }
                relationships.append(relationship)
                
        # Write JSON output
        with open(output_file, 'w') as outfile:
            json.dump({
                'control_cause_relationships': relationships,
                'export_summary': {
                    'total_count': len(relationships),
                    'export_date': datetime.now().isoformat(),
                    'source_file': input_file
                }
            }, outfile, indent=2)
            
    except Exception as e:
        print(f"Error during JSON export: {e}")
        return 0
        
    return len(relationships)


def _matches_criteria(row: Dict[str, str], criteria: Dict[str, str]) -> bool:
    """Check if row matches filter criteria."""
    for field, value in criteria.items():
        if row.get(field, '').lower() != value.lower():
            return False
    return True


def generate_summary_report(input_file: str, output_file: str) -> None:
    """Generate summary report of Control-Cause relationships."""
    stats = {
        'total_relationships': 0,
        'control_types': {},
        'relationship_types': {},
        'unique_controls': set(),
        'unique_causes': set()
    }
    
    try:
        with open(input_file, 'r', newline='') as infile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                stats['total_relationships'] += 1
                
                # Track control types
                control_type = row.get('Control_Type', 'Unknown')
                stats['control_types'][control_type] = stats['control_types'].get(control_type, 0) + 1
                
                # Track relationship types
                rel_type = row.get('Relationship_Type', 'Standard')
                stats['relationship_types'][rel_type] = stats['relationship_types'].get(rel_type, 0) + 1
                
                # Track unique IDs
                stats['unique_controls'].add(row.get('Control_ID', ''))
                stats['unique_causes'].add(row.get('Cause_ID', ''))
                
        # Convert sets to counts for JSON serialization
        stats['unique_controls'] = len(stats['unique_controls'])
        stats['unique_causes'] = len(stats['unique_causes'])
        
        # Write summary report
        with open(output_file, 'w') as outfile:
            json.dump({
                'summary_report': stats,
                'generation_date': datetime.now().isoformat(),
                'source_file': input_file
            }, outfile, indent=2)
            
    except Exception as e:
        print(f"Error generating summary report: {e}")


def main():
    """Main entry point for legacy Control-Cause export script."""
    if len(sys.argv) < 3:
        print("Usage: ExportCCs.py <input_file> <output_file> [format] [options]")
        print("  input_file: CSV file with Control-Cause data")
        print("  output_file: Output file path")
        print("  format: csv, json, or summary (default: csv)")
        print("  options: Additional options (reserved for future use)")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    export_format = sys.argv[3].lower() if len(sys.argv) > 3 else 'csv'
    
    print(f"[LEGACY] ExportCCs: Processing {input_file}")
    print(f"[LEGACY] ExportCCs: Export format: {export_format}")
    
    if export_format == 'csv':
        count = export_control_causes_csv(input_file, output_file)
        print(f"[LEGACY] ExportCCs: Exported {count} relationships to CSV")
    elif export_format == 'json':
        count = export_control_causes_json(input_file, output_file)
        print(f"[LEGACY] ExportCCs: Exported {count} relationships to JSON")
    elif export_format == 'summary':
        generate_summary_report(input_file, output_file)
        print(f"[LEGACY] ExportCCs: Generated summary report")
    else:
        print(f"Error: Unsupported export format: {export_format}")
        sys.exit(1)
        
    print(f"[LEGACY] ExportCCs: Output written to {output_file}")


if __name__ == "__main__":
    main()