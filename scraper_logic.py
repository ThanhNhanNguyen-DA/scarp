import time, random
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Các domain hoặc chuỗi cần bỏ qua
BLACKLIST = [
    "facebook", "linkedin", "twitter", "youtube",
    "instagram", "mailto:", "tel:", ".pdf", "#"
]

# --- Auto scroll dùng cho kiểu infinite scroll ---
def auto_scroll(driver, pause=2):
    """Cuộn xuống liên tục cho đến khi không còn nội dung mới."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ---------------- LAYER 1: Lấy danh sách link ----------------
def get_links(driver, base_url, keyword_filter, page_type):
    """
    Cào toàn bộ link phù hợp với cấu trúc của site:
    - listing (chỉ 1 trang)
    - pagination (tự động lặp tới khi hết thật)
    - infinite_scroll (cuộn tới đáy)
    """
    print(f"🌍 Crawling {base_url}")
    all_links = set()

    driver.get(base_url)
    time.sleep(3)

    # --- Hàm kiểm tra link hợp lệ ---
    def is_valid(href):
        if not href:
            return False
        if any(bad in href for bad in BLACKLIST):
            return False
        return keyword_filter in href

    # --- Infinite Scroll ---
    if page_type == "infinite_scroll":
        auto_scroll(driver)

    # --- Pagination ---
    if page_type == "pagination":
        page = 1
        empty_streak = 0
        max_empty = 3        # Dừng sau 3 trang liên tiếp không có link mới
        max_pages = 999      # Giới hạn cứng để chống vòng lặp vô hạn

        while True:
            page_url = f"{base_url}?page={page}" if "?" not in base_url else f"{base_url}&page={page}"
            print(f"🔄 Visiting {page_url}")

            # --- Retry load trang ---
            for attempt in range(3):
                try:
                    driver.get(page_url)
                    time.sleep(random.uniform(2, 4))
                    break
                except Exception as e:
                    print(f"   ⚠️ Retry {attempt+1}/3 due to {e}")
                    time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            found_links = [
                urljoin(base_url, a["href"])
                for a in soup.select("a[href]")
                if is_valid(a.get("href"))
            ]

            new_links = [u for u in found_links if u not in all_links]
            all_links.update(new_links)

            print(f"   ➤ Page {page}: found={len(found_links)}, new={len(new_links)}, total={len(all_links)}")

            # --- Dừng khi 3 trang liên tiếp không có link mới ---
            if not new_links:
                empty_streak += 1
                print(f"   ⚠️ Empty page streak = {empty_streak}")
            else:
                empty_streak = 0

            if empty_streak >= max_empty:
                print("   ✅ No new links after 3 consecutive pages → stop full crawl.")
                break

            # --- Giới hạn an toàn ---
            page += 1
            if page > max_pages:
                print("   ⛔ Max pages (failsafe 999) → stop to avoid infinite loop.")
                break

        print(f"✅ Finished crawl: total {len(all_links)} links from {base_url}")

    else:
        # --- Listing / Single Page ---
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if is_valid(href):
                all_links.add(urljoin(base_url, href))
        print(f"✅ Collected {len(all_links)} links from listing page.")

    return list(all_links)


# ---------------- LAYER 2: Lấy chi tiết ----------------
def scrape_detail(driver, url):
    """Lấy nội dung HTML + meta của từng link chi tiết."""
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 4))

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1,h2,h3")
        meta = {m.get("name"): m.get("content") for m in soup.select("meta[name]")}

        return {
            "url": url,
            "title": title.get_text(strip=True) if title else "",
            "meta": meta,
            "html": html,
        }
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return {"url": url, "error": str(e)}
