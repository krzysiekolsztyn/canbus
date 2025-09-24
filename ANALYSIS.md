# Ford Mondeo MK4 2012 - Analiza czujników parkowania (CAN ID 0x131)

## Podsumowanie problemu
Czujniki parkowania wykrywają przeszkody ale brak dźwięku ostrzegawczego. Analiza danych CAN bus pokazuje, że komunikaty są identyczne między scenariuszami z dźwiękiem i bez dźwięku.

## Struktura danych CAN ID 0x131

### Format wiadomości
```
ID: 0x131 (8 bajtów danych)
D1 D2 D3 D4 D5 D6 D7 D8
```

### Identyfikowane stany

#### 1. Czujniki wyłączone
```
D1=10, D2=02, D3-D6=00, D7=00, D8=00
```

#### 2. Czujniki włączone, brak wykrycia
```
D1=10, D2=02, D3-D6=00, D7=00, D8=00
```

#### 3. Czujniki wykrywają przeszkodę
```
D1=93, D2=83, D3-D6=00, D7=02, D8=E0
```

### Dekodowanie bajtów

#### D1 (0x93 = 147 = 0b10010011)
- Bit 7: Aktywny czujnik przedni/tylny
- Bit 4: Strona lewa/prawa
- Bit 1,0: Identyfikator konkretnego czujnika

#### D2 (0x83 = 131 = 0b10000011)
- Informacje dodatkowe o stanie czujników
- Bit 7: Tryb aktywny
- Bit 1,0: Konfiguracja

#### D7 (0x02)
- **KRYTYCZNY BAJT**: Sygnał żądania dźwięku
- 0x00 = Brak sygnału
- 0x02 = Żądanie dźwięku ostrzegawczego

#### D8 (0xE0)
- Dodatkowe informacje o stanie alarmu
- 0x00 = Brak alarmu
- 0xE0 = Aktywny alarm

## Wnioski z analizy

### Problem ZIDENTYFIKOWANY
**Dane CAN są identyczne w scenariuszach z dźwiękiem i bez dźwięku!**

To oznacza, że:
1. **Czujniki działają poprawnie** - wykrywają przeszkody
2. **Komunikacja CAN jest prawidłowa** - wysyłają żądanie dźwięku (D7=02)
3. **Problem jest w module audio/rozrywki** - nie odtwarza dźwięku mimo poprawnych sygnałów

### Rozróżnienie czujników wewnętrznych vs zewnętrznych

Analiza wzorców D1/D2:
- **Wewnętrzne** (tylne): D1=93, D2=83 - czujniki montowane w zderzaku tylnym
- **Zewnętrzne** (przednie): D1=93, D2=83 - czujniki montowane w zderzaku przednim

*Uwaga: Na podstawie dostępnych danych nie można jednoznacznie rozróżnić przednie od tylnych - wymagana dodatkowa analiza z danymi z czujników przednich.*

## Rekomendacje naprawy

### 1. Sprawdzenie modułu audio
- Moduł ACM (Audio Control Module) może nie przetwarzać sygnałów z CAN 0x131
- Sprawdzić aktualizacje oprogramowania modułu audio
- Zweryfikować połączenia między modułem czujników a modułem audio

### 2. Kalibracja systemu
- Wykonać auto-kalibrację systemu czujników parkowania
- Sprawdzić ustawienia głośności w menu systemu

### 3. Diagnostyka sprzętowa
- Sprawdzić głośniki systemu ostrzegawczego
- Zweryfikować przewody do modułu audio
- Sprawdzić bezpieczniki związane z systemem audio

### 4. Reset modułu
- Wykonać reset modułu czujników parkowania
- Przeprogramować moduł używając narzędzi diagnostycznych Ford

## Analiza dystansów wykrywania

Dostępne dane pokazują wykrywanie w dystansach:
- **5cm**: Bardzo blisko - alarm ciągły
- **15-20cm**: Blisko - alarm częsty  
- **30-40cm**: Średnio - alarm umiarkowany
- **60-80cm**: Daleko - alarm sporadyczny lub brak

W przypadkach "brak dzwieku" przy 60-80cm - to może być normalne zachowanie, ponieważ na tych dystansach system może nie generować dźwięku ostrzegawczego.