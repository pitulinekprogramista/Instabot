# Instaling Bot

Automatyczny bot do nauki słówek na Instaling.  
Bot wpisuje słówka, uczy się na błędach i prowadzi statystyki.

---

## Wymagania

- Windows 10 (64-bit)  
- Python 3.12+ (https://www.python.org/downloads/)  
- Chrome (aktualna wersja)  
- Visual Studio Code (opcjonalnie, dla wygodnego uruchamiania)  

---

## Instalacja pakietów

1. Otwórz terminal w folderze projektu (InstaBot).  
2. Zainstaluj wymagane biblioteki:

```
pip install selenium googletrans==4.0.0-rc1
```

3. Sprawdź, że `chromedriver.exe` jest w tym samym folderze co `instabot.py`.
- `selenium` – do sterowania przeglądarką Chrome.  
- `googletrans==4.0.0-rc1` – do tłumaczenia słówek.  
Pobierz odpowiednią wersję ChromeDriver: https://chromedriver.chromium.org/downloads

---

## Konfiguracja

W pliku `instabot` wpisz swój login i hasło:

```
EMAIL = "twoj_login"
PASSWORD = "twoje_haslo"
```
---

## Uruchomienie bota

1. Otwórz terminal w folderze projektu.  
2. Uruchom skrypt:

```
python instabot.py
```

3. Bot automatycznie wpisze login i hasło.  ( Być może bedzie potrzebne zaakcepowanie plików cookies instalinga)
4. Kliknij rozpocnij lekcje.  
5. A terminalu wciśnij ENTER, aby rozpocząć speedrun lekcji.  

---

## Jak działa bot

- Bot pobiera słówko do przetłumaczenia.  
- Jeśli zna tłumaczenie z `slownik.json`, wpisuje od razu.  
- Jeśli nie zna, używa Google Translate (PL → EN).  
- Po odpowiedzi sprawdza poprawność i uczy się na błędach, zapisując poprawną formę w `slownik.json`.  
- Prowadzi statystyki w `statystyki.json` (liczba uruchomień i słówek rozwiązanych).  

---

## Uwagi

- Logi Chrome (np. PHONE_REGISTRATION_ERROR, DevTools listening) mogą pojawiać się w terminalu – są normalne i nie wpływają na działanie bota.  
- Nie używamy środowiska wirtualnego (`venv`), więc pakiety Python są globalne.
- Bot na początku bedzie sie mylić a czasami uznaję własne poprawne odpowiedzi za błędne, nie wpływa to na działanie bota

---

## Plany na przyszłość

- Dodać opóźnienia (`time.sleep`) lub randomizację, aby bot wyglądał bardziej naturalnie.  
- Rozszerzyć statystyki lub dodać „Turbo Level / Rank” w konsoli.  

---

## Autor

Junior

## Odpowiedzialność

Metoda sprawdzona w praktyce, lecz w przyszłości Instaling może zmienić layout lub wprowadzić zabezpieczenia.  
Bot może wtedy przestać działać.  

Nie biorę odpowiedzialności za ewentualne konsekwencje korzystania z programu – używasz go na własną odpowiedzialność.
