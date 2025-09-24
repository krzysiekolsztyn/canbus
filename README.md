# Ford Mondeo MK4 2012 - CAN Bus Parking Sensors Analysis

## Opis problemu
Repozytorium zawiera dane CAN bus z czujników parkowania Ford Mondeo MK4 2012 (ID 0x131). Główny problem to brak dźwięku ostrzegawczego mimo poprawnego wykrywania przeszkód przez czujniki.

## Struktura danych

### Pliki CSV
Każdy plik zawiera dane w formacie:
```
Time Stamp,ID,Extended,Dir,Bus,LEN,D1,D2,D3,D4,D5,D6,D7,D8
```

### Kategorie plików:
- **`131 wyloczony czujniki.csv`** - Czujniki wyłączone
- **`131 wloczony czujniki.csv`** - Czujniki włączone, brak wykrycia
- **`131 [pozycja] [dystans] [strona] [numer].csv`** - Aktywne wykrywanie
- **`131 [pozycja] [dystans] [strona] brak dzwieku [numer].csv`** - Wykrywanie bez dźwięku

## Analiza danych CAN ID 0x131

### Kluczowe bajty:
- **D1, D2**: Identyfikacja czujników i ich stanu
- **D7**: **KRYTYCZNY** - Żądanie sygnału dźwiękowego
  - `0x00` = Brak żądania dźwięku
  - `0x02` = Żądanie dźwięku ostrzegawczego
- **D8**: Dodatkowe informacje o alarmie

### Zidentyfikowane wzorce:

#### Czujniki wyłączone:
```
D1=10, D2=02, D3-D6=00, D7=00, D8=00
```

#### Czujniki włączone, brak wykrycia:
```
D1=93, D2=83, D3-D6=00, D7=00, D8=00
```

#### Czujniki wykrywają przeszkodę:
```
D1=93, D2=83, D3-D6=00, D7=02, D8=E0
```

## 🔍 Kluczowe odkrycie

**Analiza plików "brak dzwieku" pokazuje identyczne dane CAN jak pliki z działającym dźwiękiem!**

To oznacza:
- ✅ Czujniki działają poprawnie
- ✅ Komunikacja CAN jest prawidłowa  
- ✅ Sygnał żądania dźwięku (D7=02) jest wysyłany
- ❌ **Problem jest w module audio pojazdu**

## Rozwiązania

### 1. Sprawdzenie ustawień audio
- Sprawdź głośność systemu ostrzeżeń w menu pojazdu
- Upewnij się, że dźwięki parkowania nie są wyciszone

### 2. Reset modułu czujników
```
1. Wyłącz zapłon
2. Odłącz akumulator na 15 minut
3. Podłącz akumulator
4. Uruchom pojazd i przetestuj czujniki
```

### 3. Diagnostyka serwisowa
- Sprawdzenie modułu ACM (Audio Control Module)
- Aktualizacja oprogramowania modułów
- Kalibracja systemu czujników parkowania

### 4. Sprawdzenie sprzętowe
- Test głośników ostrzegawczych
- Weryfikacja przewodów do modułu audio
- Kontrola bezpieczników systemu audio

## Narzędzia analizy

### `canbus_analyzer.py`
Skrypt Python do analizy plików CSV:

```bash
# Analiza wszystkich plików
python3 canbus_analyzer.py

# Analiza konkretnego pliku
python3 canbus_analyzer.py "nazwa_pliku.csv"
```

### Funkcje analizatora:
- Parsowanie danych CAN ID 0x131
- Identyfikacja stanów czujników
- Analiza wzorców dźwiękowych
- Dekodowanie pozycji czujników
- Raportowanie problemów

## Interpretacja wyników

### Rozróżnienie czujników:
- **D1 bit 7**: Aktywacja systemu
- **D1 bit 4**: Strona (lewa/prawa)
- **D1 bit 1,0**: Numer czujnika

### Dystanse wykrywania:
- **5-15cm**: Alarm ciągły (bardzo blisko)
- **20-40cm**: Alarm częsty (blisko)  
- **60-80cm**: Alarm sporadyczny (daleko/brak dźwięku to normalne)

## Dokumentacja techniczna

Zobacz plik `ANALYSIS.md` dla szczegółowej analizy technicznej i wzorców danych.

---

**Wniosek**: Problem nie leży w czujnikach ani komunikacji CAN, ale w przetwarzaniu sygnału przez moduł audio pojazdu. Zalecana konsultacja z autoryzowanym serwisem Ford.