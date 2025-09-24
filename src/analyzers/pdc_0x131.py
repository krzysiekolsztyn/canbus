"""
Park Distance Control (PDC) Analyzer for CAN ID 0x131

This module decodes 8-byte PDC messages from arbitration ID 0x131.
Based on analysis of real vehicle data from Polish test files.
"""

from typing import Dict, Any, Optional, Union, List
import struct


class PDCAnalyzer:
    """
    Analyzer for Park Distance Control (PDC) CAN messages with ID 0x131.
    
    Decodes 8-byte payloads containing sensor distance measurements,
    system status, and beeper control information.
    """
    
    CAN_ID = 0x131
    PAYLOAD_LENGTH = 8
    
    # Distance scaling factors (based on analysis of test data)
    # TODO: Verify exact scaling through additional captures
    DISTANCE_SCALE_FACTOR = 1.0  # Raw values appear to be in some unit
    
    def __init__(self):
        """Initialize the PDC analyzer."""
        self._last_decoded = None
    
    def can_analyze(self, can_id: int) -> bool:
        """
        Check if this analyzer can handle the given CAN ID.
        
        Args:
            can_id: CAN arbitration ID
            
        Returns:
            True if this analyzer handles the given ID
        """
        return can_id == self.CAN_ID
    
    def decode(self, payload: Union[bytes, List[int]]) -> Dict[str, Any]:
        """
        Decode a PDC message payload.
        
        Args:
            payload: 8-byte CAN payload as bytes or list of integers
            
        Returns:
            Dictionary containing decoded signals
            
        Raises:
            ValueError: If payload length is incorrect
        """
        if isinstance(payload, list):
            if len(payload) != self.PAYLOAD_LENGTH:
                raise ValueError(f"Expected {self.PAYLOAD_LENGTH} bytes, got {len(payload)}")
            payload = bytes(payload)
        elif isinstance(payload, bytes):
            if len(payload) != self.PAYLOAD_LENGTH:
                raise ValueError(f"Expected {self.PAYLOAD_LENGTH} bytes, got {len(payload)}")
        else:
            raise ValueError("Payload must be bytes or list of integers")
        
        # Convert to list for easier processing
        data = list(payload)
        
        # Based on analysis of test data patterns:
        # Disabled sensors: [10, 02, 00, 00, 00, 00, 00, 00]
        # Active sensors: [93, 83, 00, 00, 00, 00, 02, E0] (147, 131, 0, 0, 0, 0, 2, 224)
        
        result = {
            'can_id': self.CAN_ID,
            'raw_data': data,
            'system_enabled': self._decode_system_status(data),
            'sensor_distances': self._decode_sensor_distances(data),
            'beeper_status': self._decode_beeper_status(data),
            'error_flags': self._decode_error_flags(data),
            'unknown_fields': self._decode_unknown_fields(data)
        }
        
        self._last_decoded = result
        return result
    
    def _decode_system_status(self, data: List[int]) -> Dict[str, Any]:
        """
        Decode system status from the payload.
        
        Based on pattern analysis:
        - Disabled sensors: byte 0 = 0x10 (16), byte 1 = 0x02 (2)
        - Active sensors: byte 0 = 0x93 (147), byte 1 = 0x83 (131)
        """
        byte0, byte1 = data[0], data[1]
        
        # TODO: Verify these interpretations with additional test data
        system_enabled = not (byte0 == 0x10 and byte1 == 0x02)
        
        return {
            'enabled': system_enabled,
            'status_byte_0': byte0,
            'status_byte_1': byte1,
            'status_hex': f"{byte0:02X} {byte1:02X}"
        }
    
    def _decode_sensor_distances(self, data: List[int]) -> Dict[str, Any]:
        """
        Decode sensor distance measurements.
        
        TODO: Determine exact sensor mapping and distance calculation.
        The test data filenames suggest distances but exact byte mapping needs validation.
        """
        # Based on analysis, bytes 2-5 appear to be mostly zero in test data
        # This suggests sensor distances might be encoded differently
        # or these bytes serve other purposes
        
        distances = {
            'front_left': None,    # TODO: Map to specific bytes
            'front_center': None,  # TODO: Map to specific bytes  
            'front_right': None,   # TODO: Map to specific bytes
            'rear_left': None,     # TODO: Map to specific bytes
            'rear_center': None,   # TODO: Map to specific bytes
            'rear_right': None,    # TODO: Map to specific bytes
        }
        
        # Bytes 2-5 analysis (mostly zeros in test data)
        sensor_data_bytes = data[2:6]
        
        return {
            'distances_cm': distances,
            'raw_sensor_bytes': sensor_data_bytes,
            'sensor_data_hex': ' '.join(f"{b:02X}" for b in sensor_data_bytes)
        }
    
    def _decode_beeper_status(self, data: List[int]) -> Dict[str, Any]:
        """
        Decode beeper/audio warning status.
        
        Based on test data with "brak dzwieku" (no sound) in filenames,
        bytes 6-7 might control audio warnings.
        Active pattern: byte 6 = 0x02, byte 7 = 0xE0 (224)
        Disabled pattern: byte 6 = 0x00, byte 7 = 0x00
        """
        byte6, byte7 = data[6], data[7]
        
        # TODO: Verify beeper control interpretation
        beeper_active = not (byte6 == 0x00 and byte7 == 0x00)
        
        return {
            'beeper_enabled': beeper_active,
            'beeper_byte_6': byte6,
            'beeper_byte_7': byte7,
            'beeper_pattern': f"{byte6:02X} {byte7:02X}"
        }
    
    def _decode_error_flags(self, data: List[int]) -> Dict[str, Any]:
        """
        Decode error and diagnostic flags.
        
        TODO: Identify specific error conditions and their bit patterns.
        """
        # Analysis of all 8 bytes for potential error indicators
        error_indicators = []
        
        # Check for known error patterns
        # This will need to be refined with actual error condition data
        
        return {
            'has_errors': len(error_indicators) > 0,
            'error_codes': error_indicators,
            'diagnostic_info': 'No errors detected'  # TODO: Implement error detection
        }
    
    def _decode_unknown_fields(self, data: List[int]) -> Dict[str, Any]:
        """
        Document unknown or uncertain fields for future analysis.
        """
        return {
            'full_payload_hex': ' '.join(f"{b:02X}" for b in data),
            'notes': [
                'Bytes 0-1: System status/enable flags',
                'Bytes 2-5: Sensor data (mostly zeros in test samples)',
                'Bytes 6-7: Beeper/audio control',
                'Distance encoding method needs verification',
                'Sensor position mapping requires validation'
            ]
        }
    
    def analyze_csv_line(self, csv_line: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a line from a CAN CSV file.
        
        Expected format: Time Stamp,ID,Extended,Dir,Bus,LEN,D1,D2,D3,D4,D5,D6,D7,D8
        
        Args:
            csv_line: Single line from CAN CSV file
            
        Returns:
            Decoded message data or None if line doesn't match expected format
        """
        try:
            parts = [p.strip().rstrip(',') for p in csv_line.split(',')]
            
            if len(parts) < 14:  # Need at least timestamp through D8
                return None
                
            # Parse CAN ID (remove leading zeros and convert from hex)
            can_id_str = parts[1].lstrip('0') or '0'
            can_id = int(can_id_str, 16)
            
            if can_id != self.CAN_ID:
                return None
                
            # Extract data bytes D1-D8
            data_bytes = []
            for i in range(6, 14):  # D1 through D8
                if i < len(parts) and parts[i]:
                    data_bytes.append(int(parts[i], 16))
                else:
                    data_bytes.append(0)
            
            # Add CSV metadata to result
            result = self.decode(data_bytes)
            result['csv_metadata'] = {
                'timestamp': parts[0] if parts[0] else '0',
                'extended': parts[2].lower() == 'true' if len(parts) > 2 else False,
                'direction': parts[3] if len(parts) > 3 else 'Unknown',
                'bus': parts[4] if len(parts) > 4 else '0',
                'length': int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 8
            }
            
            return result
            
        except (ValueError, IndexError) as e:
            # Invalid line format
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the analyzer capabilities and current state.
        """
        return {
            'analyzer_name': 'PDC Park Distance Control',
            'can_id': f"0x{self.CAN_ID:03X}",
            'payload_length': self.PAYLOAD_LENGTH,
            'last_decoded': self._last_decoded is not None,
            'capabilities': [
                'System enable/disable detection',
                'Beeper status monitoring', 
                'Raw sensor data extraction',
                'CSV file processing',
                'Error flag detection (TODO)',
                'Distance measurement (TODO - needs calibration)'
            ],
            'limitations': [
                'Distance calculation needs verification',
                'Sensor position mapping incomplete',
                'Error conditions not fully decoded',
                'Scaling factors require validation'
            ]
        }


# Convenience function for direct usage
def analyze_pdc_message(payload: Union[bytes, List[int]]) -> Dict[str, Any]:
    """
    Convenience function to analyze a single PDC message.
    
    Args:
        payload: 8-byte CAN payload
        
    Returns:
        Decoded message data
    """
    analyzer = PDCAnalyzer()
    return analyzer.decode(payload)


def analyze_pdc_csv_file(file_path: str, max_messages: int = 100) -> List[Dict[str, Any]]:
    """
    Analyze a CSV file containing PDC messages.
    
    Args:
        file_path: Path to CSV file
        max_messages: Maximum number of messages to process
        
    Returns:
        List of decoded messages
    """
    analyzer = PDCAnalyzer()
    results = []
    
    try:
        with open(file_path, 'r') as f:
            # Skip header line
            next(f, None)
            
            for i, line in enumerate(f):
                if i >= max_messages:
                    break
                    
                result = analyzer.analyze_csv_line(line.strip())
                if result:
                    results.append(result)
                    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing file: {e}")
    
    return results