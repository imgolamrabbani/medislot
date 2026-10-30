"""End-to-end UI test: a real (headless) Chrome books an appointment."""
import threading
import time

import pytest
import uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.main import create_app
from tests.conftest import SLOT

PORT = 8765


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    app = create_app(str(tmp_path_factory.mktemp("ui") / "ui.db"))
    srv = uvicorn.Server(uvicorn.Config(app, port=PORT, log_level="error"))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    yield f"http://127.0.0.1:{PORT}"
    srv.should_exit = True


@pytest.fixture
def browser():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1100,700")
    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()


@pytest.mark.ui
def test_patient_can_book_from_web_page(server, browser):
    import httpx
    httpx.post(f"{server}/patients", json={"name": "Rahim Uddin", "phone": "01712345678", "age": 65})
    httpx.post(f"{server}/doctors", json={"name": "Dr. Nasrin", "specialty": "Cardiology", "fee": 800})

    browser.get(server)
    wait = WebDriverWait(browser, 5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#doctor option")))
    browser.execute_script(f"document.getElementById('slot').value = '{SLOT}'")
    browser.find_element(By.ID, "book").click()

    wait.until(EC.text_to_be_present_in_element((By.ID, "msg"), "Booked!"))
    row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#rows tr"))).text
    assert "Rahim Uddin" in row and "Dr. Nasrin" in row and "560" in row

    browser.find_element(By.ID, "book").click()          # same slot again
    wait.until(EC.text_to_be_present_in_element((By.ID, "msg"), "Slot already booked"))
