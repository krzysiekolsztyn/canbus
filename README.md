# canbus

A CAN bus message parsing and analysis tool.

## CLI Usage

The CLI tool allows you to parse and display CAN bus messages:

```bash
python src/cli.py message <can_id> [data_bytes...]
```

### Examples

Parse a CAN message with ID 0x131 and 8 data bytes:
```bash
python src/cli.py message 0x131 93 83 00 00 00 00 02 E0
```

Parse a message with no data bytes:
```bash
python src/cli.py message 0x123
```

### Parameters

- `can_id`: CAN message identifier (supports hex format like `0x131` or decimal like `305`)
- `data_bytes`: Optional data bytes in hexadecimal format (0-8 bytes, each 00-FF)

### Help

Use `--help` to see available commands and options:
```bash
python src/cli.py --help
python src/cli.py message --help
```