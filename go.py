from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Установка или обновление ChromeDriver
driver_path = ChromeDriverManager().install()

# Создание экземпляра драйвера с использованием Service
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Проверка работы
driver.get("https://www.google.com")
print("ChromeDriver успешно обновлен и работает!")

# Закрытие браузера
driver.quit()