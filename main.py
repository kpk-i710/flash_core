import os
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import threading

from bot import send_telegram_message

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_chromium():
    system = platform.system().lower()  # Определяем операционную систему

    if system == "linux":
        # Путь к Chromium на Linux
        chromium_path = "/usr/bin/chromium-browser"  # Используем найденный путь
        if os.path.exists(chromium_path):
            logging.info(f"Используем Chromium по пути: {chromium_path}")
            return chromium_path
        else:
            logging.error("Chromium не найден. Пожалуйста, установите Chromium вручную.")
            exit(1)

    elif system == "darwin":  # macOS
        # Путь к Google Chrome на macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            logging.info(f"Используем Google Chrome по пути: {chrome_path}")
            return chrome_path
        else:
            logging.error("Chromium не найден. Пожалуйста, установите Chromium вручную.")
            exit(1)

# Настройка Chromium
CHROMIUM_PATH = setup_chromium()

# Настройка опций для Chromium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме без отображения окна
chrome_options.add_argument("--no-sandbox")  # Отключаем sandbox
chrome_options.add_argument("--disable-dev-shm-usage")  # Отключаем использование /dev/shm
chrome_options.add_argument("--remote-debugging-port=9222")  # Включаем удаленную отладку
chrome_options.add_argument("--window-size=1920,1080")  # Устанавливаем размер окна
chrome_options.binary_location = CHROMIUM_PATH  # Указываем путь к Chromium

# Указываем путь к драйверу вручную (замените на ваш путь)
DRIVER_PATH = "/usr/local/bin/chromedriver"  # Укажите путь к chromedriver

# Проверка наличия драйвера
if not os.path.exists(DRIVER_PATH):
    logging.error(f"Драйвер не найден по пути: {DRIVER_PATH}")
    exit(1)

# Создаем сервис для драйвера
service = Service(DRIVER_PATH)

# Создаем драйвер
driver = webdriver.Chrome(service=service, options=chrome_options)

# Глобальная переменная для хранения всех матчей
all_matches = []



try:
    # Открываем сайт
    logging.info(f"Запрос к сайту начат в: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    driver.get("https://www.flashscore.com.ua/tennis/")

    # Закрываем баннер с куками
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_button.click()
        logging.info("Cookie banner closed")
    except Exception as e:
        logging.warning(f"Cookie banner not found, continuing: {e}")

    # Ждем загрузки фильтров
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "filters__group"))
    )

    # Ищем кнопку "LIVE" и кликаем по ней
    live_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'filters__tab')]/div[text()='LIVE']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", live_button)
    driver.execute_script("arguments[0].click();", live_button)
    logging.info("Clicked on LIVE tab")


    # Основной цикл для парсинга лайв-матчей
    while True:
        try:
            # Ждем загрузки матчей
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "event__match"))
            )

            # Получаем все матчи на странице
            matches = driver.find_elements(By.CLASS_NAME, "event__match")
            all_matches.clear()  # Очищаем список перед новым парсингом

            for match in matches:
                try:
                    # Получаем имена игроков
                    players = match.find_elements(By.CLASS_NAME, "event__participant")
                    if len(players) < 2:
                        continue
                    player1 = players[0].text.strip()
                    player2 = players[1].text.strip()

                    # Получаем статус матча (сеты или завершен)
                    stages = match.find_elements(By.CLASS_NAME, "event__stage--block")
                    match_status = [stage.text.strip() for stage in stages]

                    # Проверяем, содержит ли статус слово "мед" (в любом регистре)
                    if any("мед" in status.lower() for status in match_status):
                        # Формируем сообщение для отправки
                        message = f"{player1} vs {player2} - Статус: {', '.join(match_status)}"
                        # Отправляем сообщение в Telegram
                        send_telegram_message(message)

                    # Добавляем матч в список с его статусом
                    all_matches.append(f"{player1} vs {player2} - Статус: {', '.join(match_status)}")

                except Exception as e:
                    logging.error(f"Ошибка при обработке матча: {e}")

            # Вывод списка всех матчей
            logging.info("Лайв-матчи:")
            for match in all_matches:
                logging.info(match)

            # Пауза перед следующим запросом (например, 10 секунд)
            time.sleep(10)

        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")
            break

finally:
    # Закрываем браузер после завершения
    if driver:
        driver.quit()
        # sfd