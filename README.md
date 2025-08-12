# FM&C Agent
The FM&C Automation Agent is a Python-based command-line tool designed to automate updates to the FM&C Modification Template.xlsm.
It reads multiple operation-specific sheets, validates structure and data, executes RV&S (Windchill) CLI commands, and logs results back into the same Excel file.

This eliminates repetitive manual updates, reduces human error, and ensures a full audit trail.

## Features
- **Excel validation**: Ensures required sheets/columns exist before execution with strict row-level enforcement
- **Plan command**: Generate side-effect-free execution plans via JSON output
- **Operation registry**: Centralized command templating system for extensibility  
- **Multiple operations**: Supports all FM&C modification operations in the template:
  - Create/Revise Failure Modes
  - Remove Functions, Ratings, Mechanisms
  - Create/Revise/Delete Causes
  - Add/Remove Tasks from Causes
- **Dry run mode**: Preview operations without changing RV&S data (default behavior)
- **Selective execution**: Run all or only selected operations
- **Change Log**: Appends an audit sheet with timestamp, WWID, operation, result, created ID, and CLI output
- **Error taxonomy**: Controlled exit codes for different error conditions
- **CI/CD ready**: Automated testing and linting with GitHub Actions

## Requirements

- Python 3.9+
- Dependencies (installed automatically):
  - pandas >= 1.3.0
  - openpyxl >= 3.0.0  
  - typer >= 0.9.0
  - rich >= 10.0.0
- Access to the RV&S CLI executable in your system PATH
- FM&C Modification Template .xlsm file

## Installation

Clone the repo and install:

```bash
git clone https://github.com/nessawessa/FMC-agent.git
cd FMC-agent
pip install -e .
```

For development:
```bash
pip install -e .[dev]
```

## Usage

### Plan Command (New)
Generate an execution plan without making any changes:

```bash
# Generate plan for all operations
fmc plan --file "FMC Modification Template.xlsm"

# Generate plan for specific operations
fmc plan --file "template.xlsm" --ops "Create Fail Modes" "Create Causes"

# Save plan to file
fmc plan --file "template.xlsm" --output plan.json
```

The plan command outputs JSON with the following structure:
```json
{
  "operations": [
    {
      "operation": "Create Fail Mode",
      "sheet": "Create Fail Modes", 
      "row": 2,
      "command": "rvs create-failmode --function-id \"F001\" ...",
      "input_data": {
        "Function ID": "F001",
        "Description": "Test failure mode",
        "Severity": "High"
      }
    }
  ]
}
```

### Run Command  
Execute operations and append change log entries:

```bash
# Run all operations (dry-run by default)
fmc run --file "FMC Modification Template.xlsm"

# Run specific operations
fmc run --file "template.xlsm" --ops "Create Fail Modes" "Create Causes"

# Disable dry-run (when ready for real execution)
fmc run --file "template.xlsm" --no-dry-run
```

### Difference Between Plan and Run
- **Plan**: Validates workbook, generates execution plan, outputs JSON. No change log entries created.
- **Run**: Validates workbook, executes operations (dry-run by default), appends change log entries.

## Configuration

Create `fmc.toml` or `.fmc.toml` in your working directory:

```toml
rv_s_server = "your-rvs-server.example.com"
dry_run = false
json_logging = false
```

Environment variables override file configuration:
- `FMC_RVS_SERVER`
- `FMC_DRY_RUN` 
- `FMC_JSON_LOGGING`

## Operation Registry

The operation registry provides a centralized system for defining operations and their command templates. To add new operations:

1. Create an `OperationTemplate` with sheet name, required columns, and command building logic
2. Register it with the global `REGISTRY`

Example:
```python
from fmc_agent.registry import OperationTemplate, REGISTRY

template = OperationTemplate(
    sheet="My New Sheet",
    name="My New Operation", 
    required_columns=["Column1", "Column2"],
)
REGISTRY.register(template)
```

## Exit Codes

- **0**: Success
- **1**: General error (unexpected exceptions)
- **2**: Validation error (missing sheets, columns, or incomplete actionable rows)

## Validation Rules

- All required sheets must exist
- All required columns must exist in their respective sheets  
- **Row-level enforcement**: If any required column in a row has content, then ALL required columns must be populated
- Empty rows (no content in any required column) are ignored

## Development

Run tests:
```bash
pytest
```

Run linting:
```bash
ruff check .
ruff format .
```

## CI/CD

The project includes GitHub Actions workflow that:
- Runs on Python 3.9 and 3.11
- Installs dependencies
- Runs ruff linting
- Executes test suite

## License

MIT License

