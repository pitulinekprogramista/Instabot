from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from googletrans import Translator
import time, json, random, os

# ---- konfiguracja ----
LOGIN_URL = "https://instaling.pl/teacher.php?page=login"
EMAIL = "twoj_login"     # <-- wpisz swoje dane
PASSWORD = "twoje_haslo"

DB_FILE = "slownik.json"
STATS_FILE = "statystyki.json"

# ---- translator ----
translator = Translator()

# ---- pomocnicze ----
def load_dict():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_dict(d):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"runs": 0, "words": 0}

def save_stats(s):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

# ---- start selenium ----
chrome_options = Options()
chrome_options.add_argument("--log-level=3")  # ERROR only
chrome_options.add_argument("--silent")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=chrome_options)
driver.get(LOGIN_URL)
time.sleep(2)

# logowanie
driver.find_element(By.ID, "log_email").send_keys(EMAIL)
driver.find_element(By.ID, "log_password").send_keys(PASSWORD, Keys.ENTER)
print("✅ Zalogowano. Po zalogowaniu przejdź do lekcji i wciśnij ENTER tutaj, aby rozpocząć Speed Run.")
input("Naciśnij ENTER, kiedy jesteś gotowy...")

# wczytaj słownik i statystyki
slownik = load_dict()
stats = load_stats()
stats["runs"] += 1

print(f"🚀 Turbo Bot aktywowany! To już {stats['runs']} uruchomienie.")
print(f"📊 Z nami rozwiązałeś {stats['words']} słówek do tej pory.\n")

# ---- główna pętla lekcji ----
while True:
    try:
        # czekamy max 10 sekund na słówko
        word_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".translation"))
        )
        word_pl = word_el.text.strip().lower()

        # sprawdź czy znamy
        if word_pl in slownik:
            word_en = slownik[word_pl]["translation"]
        else:
            # próbujemy Google Translate (pl -> en)
            try:
                word_en = translator.translate(word_pl, src="pl", dest="en").text.lower()
            except:
                word_en = "???"

        # wpisz odpowiedź
        answer_box = driver.find_element(By.ID, "answer")
        answer_box.clear()
        answer_box.send_keys(word_en, Keys.ENTER)

        time.sleep(2)

        # sprawdź poprawną odpowiedź
        correct_word = driver.find_element(By.ID, "word").text.strip().lower()
        stats["words"] += 1

        # jeśli słowo nie jest zablokowane lub nie istnieje, zapisz/aktualizuj
        if word_pl not in slownik or not slownik[word_pl].get("locked", False):
            # domyślnie locked = False
            slownik[word_pl] = {"translation": correct_word, "locked": False}
            save_dict(slownik)
            print(f"❌ {word_pl} -> {word_en} | poprawnie: {correct_word}")
        else:
            print(f"✅ {word_pl} -> {word_en} (zablokowane, nie nadpisano)")

        # kliknij enter, żeby lecieć dalej
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ENTER)

        # randomowy delay żeby wyglądało naturalnie
        time.sleep(random.uniform(1.5, 3.5))

    except Exception as e:
        print("Koniec lekcji albo błąd:", e)
        break

# zapisz statystyki
save_stats(stats)
print(f"\n🏆 Sesja zakończona. Łącznie uruchomień: {stats['runs']}, słówek rozwiązanych: {stats['words']}.")
input("\nNaciśnij ENTER, aby zamknąć przeglądarkę...")
driver.quit()


