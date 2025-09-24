"""
Unit tests for PDC 0x131 analyzer.

Tests the Park Distance Control message decoder with sample frames
based on actual vehicle data patterns.
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzers.pdc_0x131 import PDCAnalyzer, analyze_pdc_message


class TestPDCAnalyzer(unittest.TestCase):
    """Test cases for PDC analyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = PDCAnalyzer()
    
    def test_can_analyze_correct_id(self):
        """Test that analyzer accepts correct CAN ID."""
        self.assertTrue(self.analyzer.can_analyze(0x131))
        self.assertFalse(self.analyzer.can_analyze(0x130))
        self.assertFalse(self.analyzer.can_analyze(0x132))
    
    def test_decode_disabled_sensors_pattern(self):
        """Test decoding of disabled sensors pattern from test data."""
        # Pattern from "131 wyloczony czujniki.csv" (disabled sensors)
        payload = [0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        result = self.analyzer.decode(payload)
        
        self.assertEqual(result['can_id'], 0x131)
        self.assertEqual(result['raw_data'], payload)
        
        # System should be detected as disabled
        system_status = result['system_enabled']
        self.assertFalse(system_status['enabled'])
        self.assertEqual(system_status['status_byte_0'], 0x10)
        self.assertEqual(system_status['status_byte_1'], 0x02)
        
        # Beeper should be inactive
        beeper_status = result['beeper_status']
        self.assertFalse(beeper_status['beeper_enabled'])
    
    def test_decode_active_sensors_pattern(self):
        """Test decoding of active sensors pattern from test data."""
        # Pattern from active sensor files (e.g., "131 przód 5 cm prawy 1.csv")
        payload = [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0]
        
        result = self.analyzer.decode(payload)
        
        self.assertEqual(result['can_id'], 0x131)
        self.assertEqual(result['raw_data'], payload)
        
        # System should be detected as enabled
        system_status = result['system_enabled']
        self.assertTrue(system_status['enabled'])
        self.assertEqual(system_status['status_byte_0'], 0x93)
        self.assertEqual(system_status['status_byte_1'], 0x83)
        
        # Beeper should be active
        beeper_status = result['beeper_status']
        self.assertTrue(beeper_status['beeper_enabled'])
        self.assertEqual(beeper_status['beeper_byte_6'], 0x02)
        self.assertEqual(beeper_status['beeper_byte_7'], 0xE0)
    
    def test_decode_bytes_input(self):
        """Test decoding with bytes input."""
        payload_bytes = bytes([0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0])
        result = self.analyzer.decode(payload_bytes)
        
        self.assertEqual(result['can_id'], 0x131)
        self.assertTrue(result['system_enabled']['enabled'])
    
    def test_decode_invalid_length(self):
        """Test error handling for invalid payload length."""
        with self.assertRaises(ValueError):
            self.analyzer.decode([0x93, 0x83, 0x00])  # Too short
        
        with self.assertRaises(ValueError):
            self.analyzer.decode([0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0, 0xFF])  # Too long
    
    def test_decode_invalid_type(self):
        """Test error handling for invalid payload type."""
        with self.assertRaises(ValueError):
            self.analyzer.decode("invalid")
        
        with self.assertRaises(ValueError):
            self.analyzer.decode(12345)
    
    def test_sensor_distances_structure(self):
        """Test that sensor distances are properly structured."""
        payload = [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0]
        result = self.analyzer.decode(payload)
        
        distances = result['sensor_distances']['distances_cm']
        expected_sensors = ['front_left', 'front_center', 'front_right', 
                          'rear_left', 'rear_center', 'rear_right']
        
        for sensor in expected_sensors:
            self.assertIn(sensor, distances)
            # TODO: Update these tests when distance calculation is implemented
            self.assertIsNone(distances[sensor])
    
    def test_unknown_fields_documentation(self):
        """Test that unknown fields are properly documented."""
        payload = [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0]
        result = self.analyzer.decode(payload)
        
        unknown = result['unknown_fields']
        self.assertIn('full_payload_hex', unknown)
        self.assertIn('notes', unknown)
        self.assertEqual(unknown['full_payload_hex'], '93 83 00 00 00 00 02 E0')
        self.assertIsInstance(unknown['notes'], list)
        self.assertGreater(len(unknown['notes']), 0)
    
    def test_csv_line_parsing_valid(self):
        """Test parsing valid CSV line from test data."""
        # Example line from test files
        csv_line = "0,00000131,false,Rx,0,8,93,83,00,00,00,00,02,E0,"
        
        result = self.analyzer.analyze_csv_line(csv_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['can_id'], 0x131)
        self.assertEqual(result['raw_data'], [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0])
        
        # Check CSV metadata
        metadata = result['csv_metadata']
        self.assertEqual(metadata['timestamp'], '0')
        self.assertFalse(metadata['extended'])
        self.assertEqual(metadata['direction'], 'Rx')
        self.assertEqual(metadata['bus'], '0')
        self.assertEqual(metadata['length'], 8)
    
    def test_csv_line_parsing_invalid_id(self):
        """Test that CSV lines with wrong ID are ignored."""
        csv_line = "0,00000132,false,Rx,0,8,93,83,00,00,00,00,02,E0,"
        result = self.analyzer.analyze_csv_line(csv_line)
        self.assertIsNone(result)
    
    def test_csv_line_parsing_malformed(self):
        """Test handling of malformed CSV lines."""
        malformed_lines = [
            "",  # Empty line
            "invalid,data",  # Too few fields
            "0,invalid_id,false,Rx,0,8,93,83,00,00,00,00,02,E0,",  # Invalid ID
            "0,00000131,false,Rx,0,8,XX,83,00,00,00,00,02,E0,",  # Invalid hex
        ]
        
        for line in malformed_lines:
            result = self.analyzer.analyze_csv_line(line)
            self.assertIsNone(result, f"Should return None for malformed line: {line}")
    
    def test_convenience_function(self):
        """Test the convenience function for direct message analysis."""
        payload = [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0]
        result = analyze_pdc_message(payload)
        
        self.assertEqual(result['can_id'], 0x131)
        self.assertTrue(result['system_enabled']['enabled'])
    
    def test_get_summary(self):
        """Test analyzer summary information."""
        summary = self.analyzer.get_summary()
        
        self.assertEqual(summary['analyzer_name'], 'PDC Park Distance Control')
        self.assertEqual(summary['can_id'], '0x131')
        self.assertEqual(summary['payload_length'], 8)
        self.assertFalse(summary['last_decoded'])  # No messages decoded yet
        
        self.assertIn('capabilities', summary)
        self.assertIn('limitations', summary)
        self.assertIsInstance(summary['capabilities'], list)
        self.assertIsInstance(summary['limitations'], list)
        
        # Decode a message and check summary updates
        self.analyzer.decode([0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0])
        summary_after = self.analyzer.get_summary()
        self.assertTrue(summary_after['last_decoded'])
    
    def test_multiple_decode_calls(self):
        """Test that analyzer can handle multiple decode calls."""
        payloads = [
            [0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Disabled
            [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0],  # Active
            [0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Disabled again
        ]
        
        results = []
        for payload in payloads:
            result = self.analyzer.decode(payload)
            results.append(result)
        
        # Check that each decode worked independently
        self.assertFalse(results[0]['system_enabled']['enabled'])  # Disabled
        self.assertTrue(results[1]['system_enabled']['enabled'])   # Active
        self.assertFalse(results[2]['system_enabled']['enabled'])  # Disabled
    
    def test_error_flags_structure(self):
        """Test error flags structure is present."""
        payload = [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0]
        result = self.analyzer.decode(payload)
        
        error_flags = result['error_flags']
        self.assertIn('has_errors', error_flags)
        self.assertIn('error_codes', error_flags)
        self.assertIn('diagnostic_info', error_flags)
        
        # TODO: Update when error detection is implemented
        self.assertFalse(error_flags['has_errors'])


class TestPDCAnalyzerIntegration(unittest.TestCase):
    """Integration tests with actual test data patterns."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = PDCAnalyzer()
    
    def test_real_data_patterns(self):
        """Test analyzer with patterns from actual test files."""
        # Test cases based on actual data from CSV files
        test_cases = [
            {
                'name': 'disabled_sensors',
                'payload': [0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                'expected_enabled': False,
                'expected_beeper': False
            },
            {
                'name': 'enabled_sensors_pattern_1',
                'payload': [0x93, 0x83, 0x00, 0x00, 0x00, 0x00, 0x02, 0xE0],
                'expected_enabled': True,
                'expected_beeper': True
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                result = self.analyzer.decode(case['payload'])
                
                self.assertEqual(
                    result['system_enabled']['enabled'], 
                    case['expected_enabled'],
                    f"System enabled mismatch for {case['name']}"
                )
                
                self.assertEqual(
                    result['beeper_status']['beeper_enabled'],
                    case['expected_beeper'],
                    f"Beeper status mismatch for {case['name']}"
                )


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)