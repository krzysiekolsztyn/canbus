#!/usr/bin/env python3
"""
CAN Bus Analyzer CLI Tool

Command-line interface for analyzing CAN messages, starting with PDC 0x131.
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from analyzers.pdc_0x131 import PDCAnalyzer, analyze_pdc_csv_file


def analyze_message(args):
    """Analyze a single CAN message from command line."""
    try:
        # Parse hex bytes from command line
        payload = []
        for hex_byte in args.payload:
            payload.append(int(hex_byte, 16))
        
        if len(payload) != 8:
            print(f"Error: PDC messages require exactly 8 bytes, got {len(payload)}")
            return 1
        
        analyzer = PDCAnalyzer()
        if not analyzer.can_analyze(args.can_id):
            print(f"Error: This analyzer only handles CAN ID 0x131, got 0x{args.can_id:X}")
            return 1
        
        result = analyzer.decode(payload)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_decoded_message(result)
        
        return 0
        
    except ValueError as e:
        print(f"Error parsing payload: {e}")
        return 1
    except Exception as e:
        print(f"Error analyzing message: {e}")
        return 1


def analyze_file(args):
    """Analyze a CSV file containing CAN messages."""
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return 1
        
        print(f"Analyzing PDC messages from: {file_path}")
        print("-" * 50)
        
        results = analyze_pdc_csv_file(str(file_path), max_messages=args.max_messages)
        
        if not results:
            print("No valid PDC messages found in file.")
            return 0
        
        print(f"Found {len(results)} PDC message(s)")
        print()
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for i, result in enumerate(results):
                print(f"Message {i+1}:")
                print_decoded_message(result, show_csv_metadata=True)
                print()
                
                if args.summary_only and i >= 2:  # Show first 3 messages only
                    print(f"... and {len(results) - 3} more messages")
                    break
        
        return 0
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return 1


def list_files(args):
    """List available test data files."""
    base_dir = Path(args.directory) if args.directory else Path.cwd()
    
    print(f"Available CAN data files in {base_dir}:")
    print("-" * 50)
    
    # Look for CSV files with "131" in the name
    csv_files = list(base_dir.glob("*131*.csv"))
    
    if not csv_files:
        print("No PDC test data files found.")
        return 0
    
    # Group files by type
    front_files = [f for f in csv_files if "przód" in f.name]
    rear_files = [f for f in csv_files if "tył" in f.name]
    control_files = [f for f in csv_files if any(word in f.name for word in ["wlaczony", "wylaczony"])]
    
    if control_files:
        print("\nSystem Control Files:")
        for f in sorted(control_files):
            print(f"  {f.name}")
    
    if front_files:
        print(f"\nFront Sensor Files ({len(front_files)}):")
        for f in sorted(front_files)[:5]:  # Show first 5
            print(f"  {f.name}")
        if len(front_files) > 5:
            print(f"  ... and {len(front_files) - 5} more")
    
    if rear_files:
        print(f"\nRear Sensor Files ({len(rear_files)}):")
        for f in sorted(rear_files)[:5]:  # Show first 5
            print(f"  {f.name}")
        if len(rear_files) > 5:
            print(f"  ... and {len(rear_files) - 5} more")
    
    return 0


def analyzer_info(args):
    """Show information about the PDC analyzer."""
    analyzer = PDCAnalyzer()
    summary = analyzer.get_summary()
    
    print("PDC CAN Message Analyzer Information")
    print("=" * 40)
    print(f"Analyzer: {summary['analyzer_name']}")
    print(f"CAN ID: {summary['can_id']}")
    print(f"Payload Length: {summary['payload_length']} bytes")
    print()
    
    print("Capabilities:")
    for capability in summary['capabilities']:
        print(f"  ✓ {capability}")
    print()
    
    print("Current Limitations:")
    for limitation in summary['limitations']:
        print(f"  ⚠ {limitation}")
    
    return 0


def print_decoded_message(result, show_csv_metadata=False):
    """Print a decoded message in human-readable format."""
    print(f"CAN ID: 0x{result['can_id']:03X}")
    print(f"Raw Data: {' '.join([f'{b:02X}' for b in result['raw_data']])}")
    
    # System status
    system = result['system_enabled']
    status = "ENABLED" if system['enabled'] else "DISABLED"
    print(f"System Status: {status} ({system['status_hex']})")
    
    # Beeper status
    beeper = result['beeper_status']
    beeper_status = "ACTIVE" if beeper['beeper_enabled'] else "SILENT"
    print(f"Beeper: {beeper_status} ({beeper['beeper_pattern']})")
    
    # Sensor data (when available)
    sensors = result['sensor_distances']
    if any(d is not None for d in sensors['distances_cm'].values()):
        print("Sensor Distances:")
        for sensor, distance in sensors['distances_cm'].items():
            if distance is not None:
                print(f"  {sensor}: {distance} cm")
    else:
        print(f"Sensor Data: {sensors['sensor_data_hex']} (interpretation pending)")
    
    # Error flags
    errors = result['error_flags']
    if errors['has_errors']:
        print(f"Errors: {', '.join(errors['error_codes'])}")
    
    # CSV metadata if available
    if show_csv_metadata and 'csv_metadata' in result:
        meta = result['csv_metadata']
        print(f"Timestamp: {meta['timestamp']}, Direction: {meta['direction']}, Bus: {meta['bus']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Park Distance Control (PDC) CAN Message Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single message
  python cli.py message 0x131 93 83 00 00 00 00 02 E0
  
  # Analyze messages from a CSV file
  python cli.py file "131 przód 5 cm prawy 1.csv"
  
  # List available test data files
  python cli.py list
  
  # Show analyzer information
  python cli.py info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single message analysis
    msg_parser = subparsers.add_parser('message', help='Analyze a single CAN message')
    msg_parser.add_argument('can_id', type=lambda x: int(x, 16), help='CAN ID in hex (e.g., 0x131)')
    msg_parser.add_argument('payload', nargs=8, help='8 payload bytes in hex (e.g., 93 83 00 00 00 00 02 E0)')
    msg_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    msg_parser.set_defaults(func=analyze_message)
    
    # File analysis
    file_parser = subparsers.add_parser('file', help='Analyze CAN messages from CSV file')
    file_parser.add_argument('file', help='Path to CSV file')
    file_parser.add_argument('--max-messages', type=int, default=100, help='Maximum messages to process')
    file_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    file_parser.add_argument('--summary-only', action='store_true', help='Show summary with first few messages only')
    file_parser.set_defaults(func=analyze_file)
    
    # List files
    list_parser = subparsers.add_parser('list', help='List available test data files')
    list_parser.add_argument('directory', nargs='?', help='Directory to search (default: current)')
    list_parser.set_defaults(func=list_files)
    
    # Analyzer info
    info_parser = subparsers.add_parser('info', help='Show analyzer information')
    info_parser.set_defaults(func=analyzer_info)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Call the appropriate function
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())