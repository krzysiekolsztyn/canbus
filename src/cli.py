#!/usr/bin/env python3
"""
CAN Bus CLI Tool

A command-line interface for handling CAN bus messages.
"""

import argparse
import sys
from typing import List


def parse_can_id(can_id_str: str) -> int:
    """Parse CAN ID from string (supports hex format like 0x131)."""
    try:
        if can_id_str.startswith('0x') or can_id_str.startswith('0X'):
            return int(can_id_str, 16)
        else:
            return int(can_id_str)
    except ValueError:
        raise ValueError(f"Invalid CAN ID format: {can_id_str}")


def parse_data_bytes(data_bytes: List[str]) -> List[int]:
    """Parse data bytes from hex strings."""
    parsed_bytes = []
    for byte_str in data_bytes:
        try:
            # Parse as hex (00-FF)
            byte_val = int(byte_str, 16)
            if byte_val < 0 or byte_val > 255:
                raise ValueError(f"Data byte out of range (0-255): {byte_val}")
            parsed_bytes.append(byte_val)
        except ValueError:
            raise ValueError(f"Invalid data byte format: {byte_str}")
    
    return parsed_bytes


def handle_message_command(args):
    """Handle the 'message' command."""
    # Parse CAN ID
    try:
        can_id = parse_can_id(args.can_id)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Parse data bytes
    try:
        data_bytes = parse_data_bytes(args.data_bytes)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Validate data length (CAN messages can have 0-8 data bytes)
    if len(data_bytes) > 8:
        print(f"Error: CAN message cannot have more than 8 data bytes, got {len(data_bytes)}", file=sys.stderr)
        return 1
    
    # Display the parsed message
    print(f"CAN Message:")
    print(f"  ID: 0x{can_id:X} ({can_id})")
    print(f"  Data Length: {len(data_bytes)} bytes")
    if data_bytes:
        hex_data = ' '.join(f"{b:02X}" for b in data_bytes)
        print(f"  Data: {hex_data}")
    else:
        print(f"  Data: (no data)")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CAN Bus CLI Tool",
        prog="cli.py"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Message command
    message_parser = subparsers.add_parser('message', help='Parse and display CAN bus message')
    message_parser.add_argument('can_id', help='CAN message ID (e.g., 0x131)')
    message_parser.add_argument('data_bytes', nargs='*', help='Data bytes in hex format (e.g., 93 83 00)')
    
    args = parser.parse_args()
    
    if args.command == 'message':
        return handle_message_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())