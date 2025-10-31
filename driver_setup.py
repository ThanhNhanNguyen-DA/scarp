import undetected_chromedriver as uc
import time

def get_selenium_driver(headless=True):
    """
    Hàm khởi tạo Chrome driver an toàn, chống detect và tránh lỗi WinError 6.
    """

    options = uc.ChromeOptions()

    # --- Cấu hình cơ bản ---
    if headless:
        options.add_argument("--headless=new")  # headless mode mới (ổn định hơn)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")  # giảm noise log trong console

    # --- Giúp tránh lỗi [WinError 6] ---
    # undetected_chromedriver đôi khi gọi lại quit() khi Python dọn rác => lỗi handle
    # use_subprocess=True sẽ cô lập Chrome trong process riêng => an toàn
    driver = uc.Chrome(options=options, use_subprocess=True)

    # --- Làm ấm driver (warm-up) ---
    # Một số site chặn request đầu tiên khi Chrome chưa ổn định
    try:
        driver.get("https://www.google.com")
        time.sleep(1)
    except Exception:
        pass

    return driver
