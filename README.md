# CAN Bus Message Analyzers

A collection of CAN bus message decoders and analyzers, starting with Park Distance Control (PDC) system analysis.

## Overview

This repository contains tools for analyzing CAN bus messages from automotive systems. It includes both the analyzer implementations and extensive real vehicle test data for validation.

## Features

- **PDC Analyzer (0x131)**: Park Distance Control message decoder
- **CSV Processing**: Analysis of CAN capture files  
- **CLI Tool**: Command-line interface for message analysis
- **Test Data**: Comprehensive real vehicle captures
- **Documentation**: Detailed signal analysis and reverse engineering notes

## Quick Start

### Analyze a Single Message

```bash
python src/cli.py message 0x131 93 83 00 00 00 00 02 E0
```

Output:
```
CAN ID: 0x131
Raw Data: 93 83 00 00 00 00 02 E0
System Status: ENABLED (93 83)
Beeper: ACTIVE (02 E0)
Sensor Data: 00 00 00 00 (interpretation pending)
```

### Analyze CSV Files

```bash
# Analyze messages from test data
python src/cli.py file "131 przód 5 cm prawy 1.csv" --summary-only

# List available test files
python src/cli.py list
```

### Programmatic Usage

```python
from src.analyzers.pdc_0x131 import PDCAnalyzer

analyzer = PDCAnalyzer()

# Decode raw message
payload = [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0]
result = analyzer.decode(payload)

print(f"System enabled: {result['system_enabled']['enabled']}")
print(f"Beeper active: {result['beeper_status']['beeper_enabled']}")
```

## Project Structure

```
canbus/
├── src/
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── pdc_0x131.py        # PDC message analyzer
│   └── cli.py                  # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_pdc_0x131.py       # Unit tests
├── docs/
│   └── pdc_0x131.md           # Detailed PDC analysis
├── 131*.csv                    # Real vehicle test data
└── README.md
```

## Test Data

The repository includes extensive test data captured from a real vehicle:

- **System States**: Enabled/disabled sensor conditions
- **Distance Measurements**: 5cm to 80cm obstacle detection
- **Sensor Positions**: Front and rear, left and right sensors  
- **Audio States**: With and without beeper activation
- **File Naming**: Polish descriptions indicating test conditions

Example files:
- `131 wylaczony czujniki.csv` - Disabled sensors
- `131 przód 5 cm prawy 1.csv` - Front right sensor, 5cm obstacle
- `131 tył 80 cm prawy brak dzwieku 1.csv` - Rear right, 80cm, no sound

## PDC Message Analysis (ID 0x131)

### Message Format
- **CAN ID**: 0x131 (11-bit standard)
- **Length**: 8 bytes
- **Frequency**: Periodic when system active

### Decoded Signals
- **System Status** (bytes 0-1): Enable/disable state
- **Beeper Control** (bytes 6-7): Audio warning state  
- **Sensor Data** (bytes 2-5): Raw sensor readings (format TBD)

### Known Patterns
```
Disabled: 10 02 00 00 00 00 00 00
Active:   93 83 00 00 00 00 02 E0
```

For complete analysis, see [docs/pdc_0x131.md](docs/pdc_0x131.md).

## CLI Commands

### Message Analysis
```bash
# Decode single message
python src/cli.py message 0x131 10 02 00 00 00 00 00 00

# Output as JSON
python src/cli.py message 0x131 93 83 00 00 00 00 02 E0 --json
```

### File Processing
```bash
# Analyze CSV file  
python src/cli.py file "131 przód 15cm lewy 1.csv"

# Limit message count
python src/cli.py file "131 tył 5 cm prawy 2.csv" --max-messages 10

# JSON output
python src/cli.py file "131 wylaczony czujniki.csv" --json
```

### Utility Commands
```bash
# Show analyzer info
python src/cli.py info

# List available test files
python src/cli.py list

# Show help
python src/cli.py --help
```

## Testing

Run the test suite:

```bash
python tests/test_pdc_0x131.py
```

All tests use real data patterns from the included CSV files to ensure accuracy.

## Development Status

### ✅ Completed
- Basic message structure decoding
- System enable/disable detection  
- Beeper status monitoring
- CSV file processing
- CLI interface
- Comprehensive test coverage
- Documentation

### 🚧 In Progress  
- Distance calculation algorithm
- Individual sensor position mapping
- Error condition detection

### 📋 Planned
- Additional CAN message analyzers
- Real-time capture integration
- Visualization tools
- DBC file generation

## Contributing

This project is based on reverse engineering of real vehicle CAN data. Contributions are welcome, especially:

- Additional test data from different vehicles
- Validation of distance calculation methods
- New message analyzer implementations
- Documentation improvements

## License

Open source - see repository for details.

## References

- [PDC Analysis Documentation](docs/pdc_0x131.md)
- Test data source: Real vehicle CAN captures
- CAN bus standards: ISO 11898