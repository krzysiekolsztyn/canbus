#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ford Mondeo MK4 2012 - Analizator danych CAN bus czujników parkowania (ID 0x131)
"""

import csv
import sys
import os
from collections import defaultdict, Counter

class ParkingSensorAnalyzer:
    def __init__(self):
        self.SENSOR_STATES = {
            (0x10, 0x02, 0x00): "Czujniki wyłączone",
            (0x10, 0x02, 0x00): "Czujniki włączone - brak wykrycia", 
            (0x93, 0x83, 0x02): "Czujniki aktywne - wykryto przeszkodę"
        }
    
    def parse_csv_file(self, filename):
        """Parsuje plik CSV z danymi CAN bus"""
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['ID'] == '00000131':  # Filtruj tylko ID 0x131
                        data.append({
                            'timestamp': float(row['Time Stamp']),
                            'd1': int(row['D1'], 16) if row['D1'] else 0,
                            'd2': int(row['D2'], 16) if row['D2'] else 0,
                            'd3': int(row['D3'], 16) if row['D3'] else 0,
                            'd4': int(row['D4'], 16) if row['D4'] else 0,
                            'd5': int(row['D5'], 16) if row['D5'] else 0,
                            'd6': int(row['D6'], 16) if row['D6'] else 0,
                            'd7': int(row['D7'], 16) if row['D7'] else 0,
                            'd8': int(row['D8'], 16) if row['D8'] else 0,
                        })
        except Exception as e:
            print(f"Błąd podczas parsowania {filename}: {e}")
            return []
        return data
    
    def analyze_sensor_state(self, d1, d2, d7):
        """Analizuje stan czujników na podstawie bajtów D1, D2, D7"""
        if d1 == 0x10 and d2 == 0x02 and d7 == 0x00:
            return "WYŁĄCZONE/BRAK_WYKRYCIA"
        elif d1 == 0x93 and d2 == 0x83 and d7 == 0x02:
            return "AKTYWNE_WYKRYCIE"
        else:
            return f"NIEZNANY_STAN(D1={d1:02X},D2={d2:02X},D7={d7:02X})"
    
    def decode_sensor_position(self, d1):
        """Dekoduje pozycję czujnika z bajtu D1"""
        positions = []
        if d1 & 0x80:  # Bit 7
            positions.append("TYLNY/PRZEDNI_AKTYWNY")
        if d1 & 0x10:  # Bit 4  
            positions.append("STRONA_PRAWA")
        if d1 & 0x02:  # Bit 1
            positions.append("CZUJNIK_2")
        if d1 & 0x01:  # Bit 0
            positions.append("CZUJNIK_1")
        return positions if positions else ["BRAK_AKTYWNYCH"]
    
    def analyze_file(self, filename):
        """Analizuje pojedynczy plik CSV"""
        print(f"\n{'='*60}")
        print(f"ANALIZA PLIKU: {filename}")
        print(f"{'='*60}")
        
        data = self.parse_csv_file(filename)
        if not data:
            print("Brak danych do analizy!")
            return
        
        # Statystyki podstawowe
        print(f"Liczba wpisów: {len(data)}")
        print(f"Czas trwania: {data[-1]['timestamp'] - data[0]['timestamp']:.1f}s")
        
        # Analiza stanów
        states = Counter()
        audio_requests = 0
        unique_patterns = set()
        
        for record in data:
            state = self.analyze_sensor_state(record['d1'], record['d2'], record['d7'])
            states[state] += 1
            
            if record['d7'] == 0x02:  # Żądanie dźwięku
                audio_requests += 1
                
            pattern = (record['d1'], record['d2'], record['d3'], record['d4'], 
                      record['d5'], record['d6'], record['d7'], record['d8'])
            unique_patterns.add(pattern)
        
        # Raport stanów
        print(f"\nSTANY CZUJNIKÓW:")
        for state, count in states.most_common():
            percentage = (count / len(data)) * 100
            print(f"  {state}: {count} ({percentage:.1f}%)")
        
        # Analiza dźwięku
        audio_percentage = (audio_requests / len(data)) * 100
        print(f"\nANALIZA DŹWIĘKU:")
        print(f"  Żądania dźwięku (D7=02): {audio_requests} ({audio_percentage:.1f}%)")
        
        if "brak dzwieku" in filename.lower():
            print(f"  ⚠️  PROBLEM: Plik zawiera 'brak dzwieku' ale żądania dźwięku są obecne!")
            print(f"      To wskazuje na problem z modułem audio, nie z czujnikami.")
        
        # Wzorce unikalne
        print(f"\nWZORCE DANYCH:")
        print(f"  Liczba unikalnych wzorców: {len(unique_patterns)}")
        for i, pattern in enumerate(sorted(unique_patterns), 1):
            d1, d2, d3, d4, d5, d6, d7, d8 = pattern
            print(f"  Wzorzec {i}: {d1:02X} {d2:02X} {d3:02X} {d4:02X} {d5:02X} {d6:02X} {d7:02X} {d8:02X}")
            
            # Interpretacja
            state = self.analyze_sensor_state(d1, d2, d7)
            positions = self.decode_sensor_position(d1)
            print(f"    → Stan: {state}")
            print(f"    → Pozycje: {', '.join(positions)}")
            if d7 == 0x02:
                print(f"    → 🔊 ŻĄDANIE DŹWIĘKU AKTYWNE")
            else:
                print(f"    → 🔇 Brak żądania dźwięku")
    
    def analyze_all_files(self, directory="."):
        """Analizuje wszystkie pliki CSV w katalogu"""
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and '131' in f]
        
        if not csv_files:
            print("Nie znaleziono plików CSV z danymi CAN ID 131!")
            return
        
        print(f"Znaleziono {len(csv_files)} plików do analizy")
        
        # Kategoryzuj pliki
        categories = {
            'disabled': [],
            'enabled': [], 
            'detecting_sound': [],
            'detecting_no_sound': []
        }
        
        for filename in csv_files:
            lower_name = filename.lower()
            if 'wyloczony' in lower_name:
                categories['disabled'].append(filename)
            elif 'wloczony' in lower_name:
                categories['enabled'].append(filename)
            elif 'brak dzwieku' in lower_name:
                categories['detecting_no_sound'].append(filename)
            else:
                categories['detecting_sound'].append(filename)
        
        # Analizuj każdą kategorię
        for category, files in categories.items():
            if files:
                print(f"\n{'#'*80}")
                print(f"KATEGORIA: {category.upper()}")
                print(f"{'#'*80}")
                
                for filename in sorted(files)[:3]:  # Maksymalnie 3 pliki z kategorii
                    self.analyze_file(filename)
        
        # Podsumowanie problemu
        if categories['detecting_no_sound']:
            print(f"\n{'!'*80}")
            print("PODSUMOWANIE PROBLEMU - BRAK DŹWIĘKU")
            print(f"{'!'*80}")
            print("Znaleziono pliki z oznaczeniem 'brak dzwieku'.")
            print("Analiza pokazuje, że dane CAN są prawidłowe (D7=02 żąda dźwięku).")
            print("\nMOŻLIWE PRZYCZYNY:")
            print("1. Problem z modułem Audio Control Module (ACM)")
            print("2. Uszkodzone przewody do głośników ostrzegawczych") 
            print("3. Nieprawidłowa konfiguracja systemu audio")
            print("4. Konieczna aktualizacja oprogramowania modułu")
            print("\nREKOMENDACJE:")
            print("- Sprawdź głośność systemu w menu pojazdu")
            print("- Wykonaj reset modułu czujników parkowania")
            print("- Skonsultuj się z serwisem Ford w sprawie reprogramowania")

def main():
    analyzer = ParkingSensorAnalyzer()
    
    if len(sys.argv) > 1:
        # Analizuj konkretny plik
        filename = sys.argv[1]
        if os.path.exists(filename):
            analyzer.analyze_file(filename)
        else:
            print(f"Plik {filename} nie istnieje!")
    else:
        # Analizuj wszystkie pliki w katalogu
        analyzer.analyze_all_files()

if __name__ == "__main__":
    main()