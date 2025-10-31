from driver_setup import get_selenium_driver
from scraper_logic import get_links, scrape_detail
from data_saver import save_data
import time
from config import SITES_CONFIG

def run_dynamic_scraper():
    driver = get_selenium_driver(headless=False)
    all_results = []

    try:
        for site, cfg in SITES_CONFIG.items():
            base_url = cfg["base_url"]
            keyword_filter = cfg["keyword_filter"]
            page_type = cfg["page_type"]

            print(f"\n🚀 START SCRAPING: {site}")
            print("=" * 80)

            # 1️⃣ Lấy danh sách link
            links = get_links(driver, base_url, keyword_filter, page_type)
            print(f"🔗 Total {len(links)} links found for {site}")

            # 2️⃣ Cào chi tiết từng link
            for i, link in enumerate(links, 1):
                print(f"   [{i}/{len(links)}] Scraping {link}")
                try:
                    data = scrape_detail(driver, link)
                    all_results.append(data)
                except Exception as e:
                    print(f"   ⚠️ Error scraping {link}: {e}")
                    continue

                # Giới hạn an toàn (nếu web quá lớn)
                if i >= 3000:
                    print(f"   ⚠️ Safety stop: reached 3000 links for {site}")
                    break

            # 3️⃣ Lưu dữ liệu
            save_data(site, all_results)
            print(f"✅ Done {site} → {len(all_results)} records saved.")
            all_results.clear()

            # Nghỉ nhẹ giữa các site tránh rate-limit
            time.sleep(3)

    except Exception as e:
        print(f"❌ Critical error: {e}")
    finally:
        driver.quit()
        print("\n🎯 Finished all sites successfully!")


# ======================
# CHẠY CHƯƠNG TRÌNH
# ======================
if __name__ == "__main__":
    run_dynamic_scraper()