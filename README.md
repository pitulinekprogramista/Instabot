# 🤖 Instabot

Bot do nauki słówek na instaling.pl. Wpisuje odpowiedzi, **uczy się na błędach** (zapamiętuje poprawne tłumaczenia w `slownik.json`) i prowadzi statystyki.

## Szybki start (Windows)

1. Zainstaluj [Python 3.10+](https://www.python.org/downloads/) (zaznacz **Add Python to PATH**) i Chrome.
2. Pobierz repo (**Code → Download ZIP**) i rozpakuj.
3. Kliknij dwukrotnie **`install.bat`** – doinstaluje potrzebne biblioteki.
4. Wpisz dane logowania (wybierz jedną opcję):
   - skopiuj `.env.example` jako `.env` i uzupełnij login oraz hasło, **albo**
   - nic nie rób – bot zapyta o nie w terminalu (hasło nie jest widoczne).
5. Kliknij dwukrotnie **`start.bat`**.
6. Po zalogowaniu kliknij w przeglądarce „Rozpocznij sesję", wróć do terminala i wciśnij **ENTER**.

ChromeDriver pobiera się sam, nie musisz nic ściągać ręcznie.

### Linux / macOS

```bash
pip install -r requirements.txt
python Instabot.py
```

## Opcje

```
python Instabot.py --limit 20            # zatrzymaj po 20 słówkach
python Instabot.py --delay-min 2 --delay-max 5   # wolniejsze, bardziej "ludzkie" tempo
python Instabot.py --stats               # pokaż statystyki i wyjdź
```

`Ctrl+C` w dowolnym momencie bezpiecznie zatrzymuje bota (dane są zapisywane na bieżąco).

## Jak to działa

1. Bot pobiera słówko po polsku.
2. Jeśli zna tłumaczenie – wpisuje je od razu.
3. Jeśli nie – pyta Google Translate; gdy to zawiedzie, celowo odpowiada `?`, żeby serwis pokazał poprawną formę.
4. Po każdej odpowiedzi zapisuje poprawne tłumaczenie do `slownik.json` i zlicza statystyki w `statystyki.json`.
5. Na końcu pokazuje podsumowanie sesji (skuteczność, nowe słówka).

### Bot wpadł w pętlę?

Bot ostrzeże, gdy to samo słówko wraca kilka razy z rzędu. Otwórz `slownik.json`, wpisz właściwe tłumaczenie i ustaw `"locked": true` – wtedy bot nigdy go nie nadpisze:

```json
"pies": { "translation": "dog", "locked": true }
```

## Bezpieczeństwo

- Hasło **nie jest** trzymane w kodzie. Plik `.env`, `slownik.json` i `statystyki.json` są w `.gitignore`, więc nie trafią na GitHuba.
- Uszkodzony plik JSON jest odkładany jako `.bak`, a nie kasowany.

## Testy (dla ciekawskich)

```bash
pip install pytest
python -m pytest tests
```

## Uwagi

- Logi Chrome (np. `PHONE_REGISTRATION_ERROR`, `DevTools listening`) są normalne.
- Instaling może zmienić layout strony – wtedy bot przestanie działać do czasu aktualizacji selektorów w `Instabot.py`.
- Automatyzacja nauki może łamić regulamin serwisu i grozić blokadą konta. Używasz na własną odpowiedzialność, autor nie ponosi odpowiedzialności za skutki.

## Autor

Junior
