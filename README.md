# FM&C Automation Agent

A Python CLI tool for validating and executing operations from FM&C (Failure Mode & Criticality) Modification Template workbooks. The agent automates the process of creating fail modes, causes, controls, and their relationships in RV&S systems.

## Features

- **Workbook Validation**: Validates Excel workbook structure and schema compliance
- **Operation Parsing**: Parses operation sheets into executable RV&S CLI commands  
- **Dry-Run Simulation**: Test operations safely without making actual changes
- **Change Log Management**: Maintains comprehensive audit trail of all operations
- **Rich CLI Interface**: User-friendly command-line interface with colored output
- **Flexible Operation Selection**: Execute specific operation types or all operations

## Installation

```bash
# Clone the repository
git clone https://github.com/nessawessa/FMC-agent.git
cd FMC-agent

# Install the package in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### 1. Validate a Workbook

```bash
# Basic validation
fmc validate --file "FM&C Modification Template.xlsm"

# Validation with sheet summary
fmc validate --file template.xlsm --summary
```

### 2. Execute Operations (Dry-Run)

```bash
# Dry-run all operations
fmc run --file template.xlsm --dry-run

# Dry-run specific operations
fmc run --file template.xlsm --dry-run --ops "Create Fail Modes" "Create Causes"
```

### 3. Execute Operations (Real)

```bash
# Execute all operations (with confirmation prompt)
fmc run --file template.xlsm

# Execute specific operations
fmc run --file template.xlsm --ops "Create Fail Modes"

# Skip validation before execution
fmc run --file template.xlsm --no-validate
```

### 4. View Change Log

```bash
# Show recent Change Log entries
fmc changelog --file template.xlsm

# Show more entries
fmc changelog --file template.xlsm --count 20
```

## Workbook Structure

The FM&C Modification Template workbook must contain the following sheets:

### Required Sheets

- **Create Fail Modes**: Define failure modes for functional systems
- **Create Causes**: Define causes that lead to failure modes  
- **Create Controls**: Define controls that mitigate causes
- **Create Control Causes**: Define relationships between controls and causes
- **Change Log**: Audit trail (automatically managed)

### Sheet Schemas

Each sheet requires specific columns. See [FMC_TEMPLATE_STRUCTURE.md](FMC_TEMPLATE_STRUCTURE.md) for detailed schema definitions.

#### Example: Create Fail Modes Sheet

| Functional System ID | Functional System Name | Fail Mode ID | Fail Mode Name | Fail Mode Description | Agent Status |
|---------------------|------------------------|--------------|----------------|----------------------|--------------|
| FS-001              | Engine Control System | FM-001       | Engine Overheat| Temperature exceeds limits |              |
| FS-001              | Engine Control System | FM-002       | Engine Underspeed | Fails to maintain RPM |              |

## Operation Types

### Create Fail Modes
Creates fail mode issues in RV&S with the following command template:
```bash
im createissue --type='Fail Mode' --field='Functional System ID'='{value}' --field='Name'='{value}' --field='Description'='{value}'
```

### Create Causes  
Creates cause issues linked to fail modes:
```bash
im createissue --type='Cause' --field='Fail Mode ID'='{value}' --field='Name'='{value}' --field='Description'='{value}'
```

### Create Controls
Creates control issues linked to causes:
```bash
im createissue --type='Control' --field='Control Type'='{value}' --field='Name'='{value}' --field='Description'='{value}'
```

### Create Control Causes
Creates relationships between controls and causes:
```bash
im createrelationship --type='Control-Cause' --field='Control ID'='{value}' --field='Cause ID'='{value}'
```

## Processing Logic

1. **Validation**: Checks workbook structure and schema compliance
2. **Parsing**: Reads operation sheets and generates command objects
3. **Filtering**: Skips rows marked as "Completed", "Success", or "Done" in Agent Status column
4. **Execution**: Runs RV&S CLI commands (real or simulated)
5. **ID Extraction**: Extracts generated IDs from command output using heuristic patterns
6. **Audit Trail**: Appends execution results to Change Log sheet

## Configuration

### CLI Options

- `--verbose`: Enable verbose logging
- `--debug`: Enable debug logging  
- `--help`: Show help information
- `--version`: Show version information

### Environment Variables

The agent respects standard environment variables for:
- RV&S CLI path configuration
- Authentication credentials (future enhancement)
- Proxy settings (future enhancement)

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest tests/test_cli_basic.py

# Run with coverage
pytest --cov=fmc_agent
```

### Code Quality

```bash
# Lint code
ruff check src/ tests/

# Format code  
ruff format src/ tests/

# Type checking (if mypy is installed)
mypy src/fmc_agent
```

### Creating Sample Data

```bash
# Generate sample workbook for testing
python -c "from fmc_agent.mock_data import create_sample_workbook; create_sample_workbook('sample.xlsx')"
```

## Architecture

- **CLI Layer** (`cli.py`): Typer-based command-line interface
- **Validation Layer** (`excel_validator.py`): Workbook structure validation
- **Operations Layer** (`operations.py`): Command parsing, execution, and Change Log management
- **Schema Layer** (`schemas.py`): Sheet and column definitions
- **Utilities** (`utils/`): Common helpers and utilities

## Error Handling

The agent provides comprehensive error handling:

- **Validation Errors**: Missing sheets, columns, or invalid data formats
- **Execution Errors**: RV&S CLI failures, network issues, timeouts
- **File Errors**: Locked files, permission issues, corruption
- **Recovery**: Continues processing when possible, maintains audit trail

## Roadmap

See [FMC_TEMPLATE_STRUCTURE.md](FMC_TEMPLATE_STRUCTURE.md) for the complete enhancement roadmap.

### Phase 2 (Next Release)
- Dependency verification (cross-sheet reference validation)
- Row-level status annotation with Excel styling  
- Structured RV&S output parsing
- Enhanced error handling and recovery

### Phase 3 (Future)
- Batch processing optimization
- Template version negotiation
- Plugin architecture for custom operations
- Advanced reporting and analytics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting (`pytest && ruff check`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check the [COPILOT_CONTEXT.py](COPILOT_CONTEXT.py) file for development guidance
- Review [FMC_TEMPLATE_STRUCTURE.md](FMC_TEMPLATE_STRUCTURE.md) for detailed specifications