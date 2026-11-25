"""Instabot - pomocnik do nauki słówek na instaling.pl.

Uruchomienie:  python Instabot.py   (opcje: python Instabot.py --help)
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import random
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGIN_URL = "https://instaling.pl/teacher.php?page=login"
DB_FILE = BASE_DIR / "slownik.json"
STATS_FILE = BASE_DIR / "statystyki.json"
ENV_FILE = BASE_DIR / ".env"
UNKNOWN_ANSWER = "?"  # celowo błędna odpowiedź - serwis pokaże poprawną, a bot ją zapamięta
LOOP_WARNING_AFTER = 3  # tyle razy z rzędu to samo słowo = ostrzeżenie o pętli


# ---------------------------------------------------------------- pliki / dane
def read_json(path: Path, default):
    """Wczytuje JSON. Uszkodzony plik jest odkładany na bok (.bak), żeby nie stracić danych."""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        backup = path.with_suffix(path.suffix + ".bak")
        try:
            path.replace(backup)
            print(f"⚠️  {path.name} jest uszkodzony ({e}). Kopia: {backup.name}, zaczynam od zera.")
        except OSError:
            print(f"⚠️  Nie mogę odczytać {path.name}: {e}")
        return default


def write_json(path: Path, data) -> None:
    """Zapis atomowy (plik tymczasowy + podmiana), więc awaria w trakcie nie psuje pliku."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load_dict() -> dict:
    return read_json(DB_FILE, {})


def load_stats() -> dict:
    stats = read_json(STATS_FILE, {})
    stats.setdefault("runs", 0)
    stats.setdefault("words", 0)
    return stats


def load_env_file(path: Path = ENV_FILE) -> None:
    """Minimalny parser .env (KLUCZ=wartość), bez dodatkowych bibliotek."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_credentials() -> tuple[str, str]:
    """Login/hasło: zmienne środowiskowe lub .env, a jak ich brak - pytamy w terminalu."""
    load_env_file()
    email = os.environ.get("INSTALING_LOGIN") or input("Login do Instalingu: ").strip()
    password = os.environ.get("INSTALING_PASSWORD") or getpass.getpass("Hasło (nie będzie widoczne): ")
    if not email or not password:
        sys.exit("❌ Login i hasło są wymagane.")
    return email, password


# ---------------------------------------------------------------- logika słówek
def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def apply_result(slownik: dict, word_pl: str, given: str, correct: str) -> bool:
    """Aktualizuje słownik po odpowiedzi. Zwraca True, jeśli odpowiedź była poprawna.

    Słówka z `locked: true` (ustawione ręcznie) nigdy nie są nadpisywane.
    """
    ok = normalize(given) == normalize(correct)
    entry = slownik.get(word_pl)
    if entry and entry.get("locked", False):
        return ok
    slownik[word_pl] = {"translation": normalize(correct), "locked": False}
    return ok


def make_translator():
    """Zwraca funkcję tłumaczącą pl->en albo None, gdy biblioteka nie jest zainstalowana."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("ℹ️  Brak deep-translator - nieznane słówka będą uczone metodą prób i błędów.")
        return None
    gt = GoogleTranslator(source="pl", target="en")

    def translate(word: str) -> str | None:
        try:
            result = gt.translate(word)
            return normalize(result) if result else None
        except Exception:  # sieć, limity Google itp. - nie wywracamy przez to bota
            return None

    return translate


# ---------------------------------------------------------------- selenium
def start_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--log-level=3")
    opts.add_argument("--silent")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=opts)  # Selenium 4.6+ sam pobiera ChromeDriver


def login(driver, email: str, password: str) -> None:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    driver.get(LOGIN_URL)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "log_email")))
    driver.find_element(By.ID, "log_email").send_keys(email)
    driver.find_element(By.ID, "log_password").send_keys(password, Keys.ENTER)


def run_lesson(driver, slownik: dict, stats: dict, translate, args) -> dict:
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    session = {"words": 0, "correct": 0, "wrong": 0, "learned": 0}
    last_word, repeats = None, 0

    while args.limit is None or session["words"] < args.limit:
        try:
            word_el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".translation"))
            )
        except TimeoutException:
            print("🏁 Brak kolejnego słówka - koniec lekcji.")
            break

        word_pl = normalize(word_el.text)
        repeats = repeats + 1 if word_pl == last_word else 1
        last_word = word_pl
        if repeats >= LOOP_WARNING_AFTER:
            print(f"🔁 '{word_pl}' wraca {repeats}. raz. Wpisz tłumaczenie w slownik.json i ustaw "
                  f'"locked": true.')

        known = word_pl in slownik
        if known:
            answer = slownik[word_pl]["translation"]
        else:
            answer = (translate(word_pl) if translate else None) or UNKNOWN_ANSWER

        box = driver.find_element(By.ID, "answer")
        box.clear()
        box.send_keys(answer, Keys.ENTER)

        try:
            correct = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "word"))
            ).text
        except TimeoutException:
            print(f"⚠️  Serwis nie pokazał poprawnej odpowiedzi dla '{word_pl}', pomijam.")
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
            continue

        ok = apply_result(slownik, word_pl, answer, correct)
        write_json(DB_FILE, slownik)
        stats["words"] += 1
        write_json(STATS_FILE, stats)  # zapis na bieżąco - nic nie ginie przy awarii

        session["words"] += 1
        if ok:
            session["correct"] += 1
            print(f"✅ {word_pl} -> {answer}")
        else:
            session["wrong"] += 1
            if not known:
                session["learned"] += 1
            print(f"❌ {word_pl} -> {answer} | poprawnie: {normalize(correct)}")

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
        time.sleep(random.uniform(args.delay_min, args.delay_max))

    return session


# ---------------------------------------------------------------- CLI
def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Bot do nauki słówek na instaling.pl")
    p.add_argument("--limit", type=int, help="zatrzymaj się po N słówkach")
    p.add_argument("--delay-min", type=float, default=1.5, help="min. przerwa między słówkami (s)")
    p.add_argument("--delay-max", type=float, default=3.5, help="maks. przerwa między słówkami (s)")
    p.add_argument("--stats", action="store_true", help="pokaż statystyki i wyjdź")
    args = p.parse_args(argv)
    if args.delay_min < 0 or args.delay_max < args.delay_min:
        p.error("--delay-max musi być >= --delay-min >= 0")
    return args


def print_stats(stats: dict, slownik: dict) -> None:
    locked = sum(1 for v in slownik.values() if v.get("locked"))
    print(f"📊 Uruchomień: {stats['runs']} | słówek rozwiązanych: {stats['words']} | "
          f"w słowniku: {len(slownik)} (zablokowanych: {locked})")


def main(argv=None) -> None:
    args = parse_args(argv)
    slownik, stats = load_dict(), load_stats()

    if args.stats:
        print_stats(stats, slownik)
        return

    email, password = get_credentials()
    translate = make_translator()
    driver = start_driver()
    session = None
    try:
        login(driver, email, password)
        print("✅ Zalogowano. Przejdź do lekcji (kliknij „Rozpocznij sesję”) "
              "i wciśnij ENTER tutaj, aby ruszyć.")
        input("Naciśnij ENTER, kiedy jesteś gotowy...")

        stats["runs"] += 1
        write_json(STATS_FILE, stats)
        print_stats(stats, slownik)
        print("Ctrl+C zatrzymuje bota w dowolnym momencie.\n")
        session = run_lesson(driver, slownik, stats, translate, args)
    except KeyboardInterrupt:
        print("\n⏹️  Przerwano przez użytkownika.")
    finally:
        if session:
            total = session["words"] or 1
            print(f"\n🏆 Sesja: {session['words']} słówek | poprawnie {session['correct']} "
                  f"({100 * session['correct'] // total}%) | błędnie {session['wrong']} | "
                  f"nowych w słowniku: {session['learned']}")
        print_stats(stats, slownik)
        try:
            input("\nNaciśnij ENTER, aby zamknąć przeglądarkę...")
        except (KeyboardInterrupt, EOFError):
            pass
        driver.quit()


if __name__ == "__main__":
    main()
