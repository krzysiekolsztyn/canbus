#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ford Mondeo MK4 2012 - Szybka diagnoza czujników parkowania
Prosty skrypt do identyfikacji problemu z dźwiękiem
"""

import csv
import os
import glob
from collections import Counter

def analyze_file_quick(filename):
    """Szybka analiza pliku CSV - tylko kluczowe informacje"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            audio_requests = 0
            total_records = 0
            patterns = set()
            
            for row in reader:
                if row['ID'] == '00000131':
                    total_records += 1
                    d7 = int(row['D7'], 16) if row['D7'] else 0
                    
                    if d7 == 0x02:  # Żądanie dźwięku
                        audio_requests += 1
                    
                    # Podstawowy wzorzec
                    d1 = int(row['D1'], 16) if row['D1'] else 0
                    d2 = int(row['D2'], 16) if row['D2'] else 0
                    patterns.add((d1, d2, d7))
            
            return {
                'total': total_records,
                'audio_requests': audio_requests,
                'patterns': patterns,
                'has_sound_issue': 'brak dzwieku' in filename.lower()
            }
    except Exception as e:
        print(f"Błąd: {filename} - {e}")
        return None

def main():
    print("="*70)
    print("SZYBKA DIAGNOZA CZUJNIKÓW PARKOWANIA - Ford Mondeo MK4 2012")
    print("="*70)
    
    # Znajdź pliki CSV
    csv_files = glob.glob("131*.csv")
    if not csv_files:
        print("❌ Nie znaleziono plików CSV z danymi czujników!")
        return
    
    print(f"📁 Znaleziono {len(csv_files)} plików")
    
    # Kategorie
    categories = {
        'disabled': [],
        'no_sound_issue': [],
        'sound_issue': []
    }
    
    # Analizuj pliki
    for filename in csv_files[:10]:  # Limit do 10 plików dla szybkości
        result = analyze_file_quick(filename)
        if not result:
            continue
            
        if 'wyloczony' in filename.lower():
            categories['disabled'].append((filename, result))
        elif result['has_sound_issue']:
            categories['sound_issue'].append((filename, result))
        else:
            categories['no_sound_issue'].append((filename, result))
    
    # Raport
    print("\n📋 WYNIKI ANALIZY:")
    print("-" * 70)
    
    # Sprawdź pliki z problemem dźwięku
    if categories['sound_issue']:
        print("🔊 PLIKI Z PROBLEMEM DŹWIĘKU:")
        for filename, result in categories['sound_issue'][:3]:
            audio_percent = (result['audio_requests'] / result['total'] * 100) if result['total'] > 0 else 0
            print(f"  📄 {filename}")
            print(f"     Żądania dźwięku: {result['audio_requests']}/{result['total']} ({audio_percent:.1f}%)")
            
            if result['audio_requests'] > 0:
                print(f"     ⚠️  PROBLEM ZIDENTYFIKOWANY: Żądania dźwięku są wysyłane!")
                print(f"        → Czujniki działają poprawnie")
                print(f"        → Problem w module audio pojazdu")
            else:
                print(f"     ✅ Brak żądań dźwięku - to normalne dla dużych dystansów")
        
        print("\n💡 REKOMENDACJE:")
        print("   1. Sprawdź głośność systemu w menu pojazdu")
        print("   2. Reset modułu czujników (odłącz akumulator na 15 min)")
        print("   3. Skonsultuj z serwisem Ford - problem w module audio")
    
    # Sprawdź pliki działające
    if categories['no_sound_issue']:
        print(f"\n✅ PLIKI BEZ PROBLEMU DŹWIĘKU: {len(categories['no_sound_issue'])}")
        working_file = categories['no_sound_issue'][0]
        filename, result = working_file
        audio_percent = (result['audio_requests'] / result['total'] * 100) if result['total'] > 0 else 0
        print(f"   Przykład: {filename}")
        print(f"   Żądania dźwięku: {result['audio_requests']}/{result['total']} ({audio_percent:.1f}%)")
    
    # Sprawdź wzorce
    print(f"\n🔍 ANALIZA WZORCÓW:")
    all_patterns = set()
    for category in categories.values():
        for filename, result in category:
            all_patterns.update(result['patterns'])
    
    for pattern in sorted(all_patterns):
        d1, d2, d7 = pattern
        if d1 == 0x10 and d2 == 0x02 and d7 == 0x00:
            print(f"   {d1:02X} {d2:02X} {d7:02X} → Czujniki wyłączone/brak wykrycia")
        elif d1 == 0x93 and d2 == 0x83 and d7 == 0x00:
            print(f"   {d1:02X} {d2:02X} {d7:02X} → Czujniki aktywne, brak przeszkody")
        elif d1 == 0x93 and d2 == 0x83 and d7 == 0x02:
            print(f"   {d1:02X} {d2:02X} {d7:02X} → Czujniki wykrywają - ŻĄDANIE DŹWIĘKU ✓")
        else:
            print(f"   {d1:02X} {d2:02X} {d7:02X} → Inne wzorce")
    
    print("\n" + "="*70)
    print("DIAGNOZA ZAKOŃCZONA")
    print("="*70)

if __name__ == "__main__":
    main()