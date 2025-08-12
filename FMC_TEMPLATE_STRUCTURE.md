# FM&C Template Structure and Schema Definition

This document defines the structure and schema requirements for the FM&C Modification Template workbook, derived from PRD specifications and enhanced for automation.

## Sheet Definitions

### 1. Create Fail Modes
**Purpose**: Define failure modes for functional systems.

**Required Columns**:
- `Functional System ID` - Unique identifier for the functional system
- `Functional System Name` - Human-readable name of the functional system
- `Fail Mode ID` - Unique identifier for the fail mode (will be generated if empty)
- `Fail Mode Name` - Human-readable name of the fail mode
- `Fail Mode Description` - Detailed description of the failure mode
- `Agent Status` - Processing status (empty, "Completed", "Failed", etc.)

**Optional Columns**:
- `Comments` - Additional notes or comments
- `Priority` - Priority level (High, Medium, Low)
- `Severity` - Severity classification

### 2. Create Causes
**Purpose**: Define causes that lead to failure modes.

**Required Columns**:
- `Fail Mode ID` - Reference to parent fail mode
- `Cause ID` - Unique identifier for the cause (will be generated if empty)
- `Cause Name` - Human-readable name of the cause
- `Cause Description` - Detailed description of the cause
- `Agent Status` - Processing status

**Optional Columns**:
- `Comments` - Additional notes
- `Probability` - Likelihood of occurrence
- `Impact` - Impact assessment

### 3. Create Controls
**Purpose**: Define controls that mitigate causes.

**Required Columns**:
- `Cause ID` - Reference to the cause being controlled
- `Control ID` - Unique identifier for the control (will be generated if empty)
- `Control Name` - Human-readable name of the control
- `Control Description` - Detailed description of the control
- `Control Type` - Type of control (Prevention, Detection, Mitigation)
- `Agent Status` - Processing status

**Optional Columns**:
- `Comments` - Additional notes
- `Effectiveness` - Control effectiveness rating
- `Implementation_Status` - Current implementation status

### 4. Create Control Causes
**Purpose**: Define many-to-many relationships between controls and causes.

**Required Columns**:
- `Control ID` - Reference to the control
- `Cause ID` - Reference to the cause
- `Agent Status` - Processing status

**Optional Columns**:
- `Comments` - Additional notes about the relationship
- `Relationship_Type` - Type of control-cause relationship

### 5. Change Log
**Purpose**: Audit trail of all operations performed by the agent.

**Columns** (automatically managed):
- `Timestamp` - When the operation was performed
- `Operation` - Description of the operation
- `Status` - Success/Failed status
- `Details` - Additional details (e.g., generated IDs)
- `CLI Output` - Truncated output from the RV&S CLI command

## Processing Rules

### Agent Status Column
The `Agent Status` column is used to track processing state:
- **Empty/Blank** - Ready for processing
- **"Completed"/"Success"/"Done"** - Successfully processed (will be skipped)
- **"Failed"/"Error"** - Processing failed (will be retried)
- **"Processing"** - Currently being processed

### ID Generation
- IDs can be pre-populated or left empty for auto-generation
- Generated IDs follow pattern: `{TYPE}-{YYYYMMDD}-{NNNN}`
- IDs are extracted from RV&S CLI output using heuristic patterns

### Cross-Sheet References
- `Fail Mode ID` in "Create Causes" must reference existing fail mode
- `Cause ID` in "Create Controls" must reference existing cause
- Control-Cause relationships require both IDs to exist

## Command Templates

### Create Fail Modes
```bash
im createissue --type='Fail Mode' \
  --field='Functional System ID'='{Functional System ID}' \
  --field='Name'='{Fail Mode Name}' \
  --field='Description'='{Fail Mode Description}'
```

### Create Causes
```bash
im createissue --type='Cause' \
  --field='Fail Mode ID'='{Fail Mode ID}' \
  --field='Name'='{Cause Name}' \
  --field='Description'='{Cause Description}'
```

### Create Controls
```bash
im createissue --type='Control' \
  --field='Control Type'='{Control Type}' \
  --field='Name'='{Control Name}' \
  --field='Description'='{Control Description}'
```

### Create Control Causes
```bash
im createrelationship --type='Control-Cause' \
  --field='Control ID'='{Control ID}' \
  --field='Cause ID'='{Cause ID}'
```

## Enhancement Roadmap

### Phase 1 (Current Implementation)
- [x] Basic sheet and column validation
- [x] Operation parsing and command generation
- [x] Dry-run simulation
- [x] Change Log management
- [x] CLI interface

### Phase 2 (Next Release)
- [ ] Dependency verification (cross-sheet reference validation)
- [ ] Row-level status annotation with Excel styling
- [ ] Structured RV&S output parsing
- [ ] Enhanced error handling and recovery

### Phase 3 (Future)
- [ ] Batch processing optimization
- [ ] Template version negotiation
- [ ] Plugin architecture for custom operations
- [ ] Advanced reporting and analytics

## Validation Rules

### Sheet-Level Validation
1. All required sheets must be present
2. Sheet names must match exactly (case-sensitive)
3. Required columns must be present in each sheet

### Column-Level Validation
1. Required columns cannot be completely empty
2. ID columns should follow consistent format
3. Cross-references must be valid

### Row-Level Validation (Future)
1. Required fields cannot be empty
2. ID uniqueness within sheet
3. Cross-sheet reference integrity
4. Data type validation (numbers, dates, etc.)

## Error Handling

### Validation Errors
- Missing sheets or columns
- Invalid data formats
- Cross-reference failures

### Execution Errors
- RV&S CLI command failures
- Network/connectivity issues
- Permission/authentication errors

### Recovery Strategies
- Retry failed operations
- Skip processed rows (based on Agent Status)
- Continue processing despite individual failures
- Comprehensive logging for troubleshooting