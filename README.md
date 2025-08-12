# FMC-agent
The FM&C Automation Agent is a Python-based command-line tool designed to automate updates to the FM&C Modification Template.xlsm.
It reads multiple operation-specific sheets, validates structure and data, executes RV&S (Windchill) CLI commands, and logs results back into the same Excel file.

This eliminates repetitive manual updates, reduces human error, and ensures a full audit trail.

Features
- Excel validation: Ensures required sheets/columns exist before execution.
- Multiple operations: Supports all FM&C modification operations in the template:
- Create/Revise Failure Modes
- Remove Functions, Ratings, Mechanisms
- Create/Revise/Delete Causes
- Add/Remove Tasks from Causes
- Dry run mode: Preview operations without changing RV&S data.
- Selective execution: Run all or only selected operations.
- Change Log: Appends an audit sheet with timestamp, WWID, operation, result, created ID, and CLI output.
- Dependency checks (planned): Ensure parent entities exist before child creation.


Requirements

- Python 3.9+
- Pip dependencies:
    pip install pandas openpyxl
- Access to the RV&S CLI executable in your system PATH.
- FM&C Modification Template .xlsm file.

Installation

    Clone the repo and install dependencies:

  - git clone https://github.com/your-org/fmc-automation-agent.git
  
  - cd fmc-automation-agent
  
  - pip install -r requirements.txt
  

Useage

Validate only:
    python excel_validator.py "FMC Modification Template.xlsm"
    
Run all operations:
    python cli_runner.py "FMC Modification Template.xlsm"
    
Dry run (no changes):
    python cli_runner.py "FMC Modification Template.xlsm" --dry-run
    
Run specfic operations:
    python cli_runner.py "FMC Modification Template.xlsm" --ops "Create Fail Modes" "Create Causes"

