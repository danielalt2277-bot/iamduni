# --- SETUP INSTRUCTIONS ---
# 1. Install Dependencies:
#    pip install tls_client playwright
#
# 2. Install Playwright Browsers:
#    playwright install

import asyncio
import random
import time
import threading
import tls_client
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# --- Advanced Configuration ---

# --- Proxies ---
PROXIES = [
    # "http://user:pass@proxy1.example.com:8080",
]

# --- Performance ---
MAX_THREADS = 10

# --- Behavior ---
MIN_WATCH_TIME = 5
MAX_WATCH_TIME = 12
VIEWS_PER_SESSION = 5


# --- Main Logic ---

def send_view_http(session, url):
    """(Tier 1: Fast) Sends a view using a direct HTTP request."""
    try:
        response = session.get(url, timeout_seconds=15)
        if response.status_code == 200 and "aweme_id" in response.text:
            return True, "Fast HTTP"
    except Exception as e:
        print(f"[-] Tier 1 (HTTP) failed: {e}")
    return False, "Fast HTTP"

async def send_view_playwright_desktop_async(url, proxy):
    """(Tier 2: Desktop Browser) Sends a view using a desktop browser."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, proxy={'server': proxy} if proxy else None)
            page = await browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            for _ in range(VIEWS_PER_SESSION):
                await page.goto(url, timeout=60000)
                await page.mouse.move(random.randint(0, 100), random.randint(0, 100))
                await asyncio.sleep(random.uniform(1, 3))
                await page.mouse.wheel(0, random.randint(100, 500))
                await asyncio.sleep(random.uniform(MIN_WATCH_TIME, MAX_WATCH_TIME))
            await browser.close()
            return True, "Desktop Browser"
    except Exception as e:
        print(f"[-] Tier 2 (Desktop) failed: {e}")
    return False, "Desktop Browser"

def send_view_playwright_desktop(url, proxy):
    return asyncio.run(send_view_playwright_desktop_async(url, proxy))

async def send_view_playwright_mobile_async(url, proxy):
    """(Tier 3: Mobile Browser) Sends a view using a mobile browser."""
    try:
        async with async_playwright() as p:
            browser = await p.webkit.launch(headless=True, proxy={'server': proxy} if proxy else None)
            context = await browser.new_context(**p.devices['iPhone 13'])
            page = await context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            for _ in range(VIEWS_PER_SESSION):
                await page.goto(url, timeout=60000)
                await page.swipe(random.randint(100, 200), random.randint(300, 500), random.randint(100, 200), random.randint(0, 100), steps=random.randint(5, 10))
                await asyncio.sleep(random.uniform(MIN_WATCH_TIME, MAX_WATCH_TIME))
            await browser.close()
            return True, "Mobile Browser"
    except Exception as e:
        print(f"[-] Tier 3 (Mobile) failed: {e}")
    return False, "Mobile Browser"

def send_view_playwright_mobile(url, proxy):
    return asyncio.run(send_view_playwright_mobile_async(url, proxy))


async def get_view_count_async(url):
    """Fetches the current view count of a video."""
    print("Fetching view count...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            await page.goto(url, timeout=60000)

            selector = '[data-e2e="video-views"]'
            views_element = await page.wait_for_selector(selector, timeout=30000)
            views_text = await views_element.inner_text()

            await browser.close()
            print(f"\n[+] Current view count for {url}: {views_text}\n")

    except Exception as e:
        print(f"\n[-] Could not fetch view count. Error: {e}\n")

def get_view_count(url):
    asyncio.run(get_view_count_async(url))

async def test_fingerprint_async():
    """Tests the browser's stealthiness against a detection website."""
    print("Testing browser fingerprint...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            await page.goto("https://bot.sannysoft.com", timeout=60000)
            await page.screenshot(path="fingerprint_test_results.png", full_page=True)
            print("Browser fingerprint test complete. Results saved to 'fingerprint_test_results.png'")
            await browser.close()
    except Exception as e:
        print(f"[-] Fingerprint test failed: {e}")

def test_fingerprint():
    asyncio.run(test_fingerprint_async())


def worker(url, lock, success_counter):
    """A worker thread that sends a single view using a multi-layered approach."""
    proxy = random.choice(PROXIES) if PROXIES else None

    session = tls_client.Session(client_identifier="chrome_120")
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    success, method = send_view_http(session, url)

    if not success:
        success, method = send_view_playwright_desktop(url, proxy)

    if not success:
        success, method = send_view_playwright_mobile(url, proxy)

    if success:
        with lock:
            success_counter['count'] += VIEWS_PER_SESSION if "Browser" in method else 1
            print(f"[{success_counter['count']}] Views sent successfully via {method} (Proxy: {proxy or 'Direct'})")
    else:
        print(f"[-] All methods failed for proxy: {proxy or 'Direct'}")

def main():
    print("--- TikTok View Bot ---")
    print("1: Send views to a video")
    print("2: Check the view count of a video")
    print("3: Test browser fingerprint")
    choice = input("Select an option (1, 2, or 3): ").strip()

    if choice == '1':
        url = input("Enter the TikTok video URL: ").strip()
        try:
            target = int(input("How many views to send: "))
        except ValueError:
            print("Invalid number. Please enter an integer.")
            return

        if not PROXIES:
            print("\n[WARNING] No proxies configured. Running in direct mode.\n")

        print("\n--- Checking initial view count ---")
        get_view_count(url)

        success_counter = {'count': 0}
        lock = threading.Lock()

        threads = []
        while success_counter['count'] < target:
            t = threading.Thread(target=worker, args=(url, lock, success_counter))
            threads.append(t)
            t.start()
            if len(threads) >= MAX_THREADS:
                for thread in threads:
                    thread.join()
                threads = []

        for t in threads:
            t.join()

        print(f"\n--- Task Complete ---")
        print(f"Successfully sent {success_counter['count']} out of {target} views.")
        print("\n--- Checking final view count ---")
        get_view_count(url)

    elif choice == '2':
        url = input("Enter the TikTok video URL to check: ").strip()
        get_view_count(url)

    elif choice == '3':
        test_fingerprint()

    else:
        print("Invalid option. Please restart and select 1, 2, or 3.")

if __name__ == "__main__":
    main()
