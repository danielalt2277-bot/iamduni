import asyncio
import random
import time
import threading
import tls_client
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# --- Configuration ---
PROXIES = []

# --- Logic ---

def send_view_http(session, url):
    """(Method 1: Fast) Sends a view using a direct HTTP request."""
    try:
        response = session.get(url, timeout_seconds=15)
        if response.status_code == 200 and "aweme_id" in response.text:
            return True, "Fast"
    except Exception as e:
        print(f"[-] HTTP request failed: {e}")
    return False, "Fast"

async def send_view_playwright_async(url, proxy):
    """(Method 2: Robust) Sends a view using a real browser."""
    try:
        async with async_playwright() as p:
            browser_args = []
            if proxy:
                browser_args.append(f"--proxy-server={proxy}")

            browser = await p.chromium.launch(headless=True, args=browser_args)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(5, 10))
            await browser.close()
            return True, "Robust"
    except Exception as e:
        print(f"[-] Playwright action failed: {e}")
    return False, "Robust"

def send_view_playwright(url, proxy):
    """Synchronous wrapper for the async playwright function."""
    return asyncio.run(send_view_playwright_async(url, proxy))

async def get_view_count_async(url):
    """Fetches the current view count of a video."""
    print("Fetching view count...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            selector = '[data-e2e="video-views"]'
            views_element = await page.wait_for_selector(selector, timeout=30000)
            views_text = await views_element.inner_text()

            await browser.close()
            print(f"\n[+] Current view count for {url}: {views_text}\n")

    except Exception as e:
        print(f"\n[-] Could not fetch view count. Error: {e}\n")

def get_view_count(url):
    """Synchronous wrapper for the async get_view_count function."""
    asyncio.run(get_view_count_async(url))

def worker(url, lock, success_counter):
    """A worker thread that sends a single view."""
    proxy = random.choice(PROXIES) if PROXIES else None

    session = tls_client.Session(client_identifier="chrome_120")
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    success, method = send_view_http(session, url)

    if not success:
        print("[-] Fast method failed. Falling back to robust browser-based method...")
        success, method = send_view_playwright(url, proxy)

    if success:
        with lock:
            success_counter['count'] += 1
            print(f"[{success_counter['count']}] View sent successfully via {method} method (Proxy: {proxy or 'Direct'})")
    else:
        print(f"[-] All methods failed for proxy: {proxy or 'Direct'}")

def main():
    print("--- TikTok View Bot ---")
    print("1: Send views to a video")
    print("2: Check the view count of a video")
    choice = input("Select an option (1 or 2): ").strip()

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
        for _ in range(target):
            t = threading.Thread(target=worker, args=(url, lock, success_counter))
            threads.append(t)
            t.start()
            time.sleep(random.uniform(0.5, 1.5))

        for t in threads:
            t.join()

        print(f"\n--- Task Complete ---")
        print(f"Successfully sent {success_counter['count']} out of {target} views.")
        print("\n--- Checking final view count ---")
        get_view_count(url)

    elif choice == '2':
        url = input("Enter the TikTok video URL to check: ").strip()
        get_view_count(url)

    else:
        print("Invalid option. Please restart and select 1 or 2.")

if __name__ == "__main__":
    main()
