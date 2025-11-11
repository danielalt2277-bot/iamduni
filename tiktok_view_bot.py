import asyncio
import random
import time
import threading
from playwright.async_api import async_playwright

def get_proxies():
    """
    Returns a list of proxies.
    IMPORTANT: The user must add their own proxies below.
    Playwright format: "http://user:pass@host:port"
    """
    return []

async def send_view(video_url, proxy=None):
    """
    Sends a view to the specified video using Playwright.
    """
    try:
        async with async_playwright() as p:
            browser_args = []
            if proxy:
                browser_args.append(f"--proxy-server={proxy}")

            browser = await p.chromium.launch(headless=True, args=browser_args)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(video_url, timeout=60000)

            # Simulate watch time
            await asyncio.sleep(random.uniform(5, 10))

            await browser.close()
            return True
    except Exception as e:
        print(f"[-] An error occurred while sending a view with proxy {proxy or 'direct'}: {e}")
        return False

def main():
    url = input("Enter TikTok video URL: ").strip()

    try:
        target = int(input("How many views: "))
    except ValueError:
        print("Invalid number of views.")
        return

    proxies = get_proxies()
    if not proxies:
        print("\n" + "="*50)
        print("[WARNING] NO PROXIES CONFIGURED")
        print("="*50)
        print("The script is running without proxies. This sends all requests from your IP address.")
        print("TikTok will quickly detect and block this, and the script will not work.")
        print("To fix this, you MUST add high-quality, rotating proxies to the `get_proxies` function.")
        print("="*50 + "\n")

    lock = threading.Lock()
    count = 0

    def worker():
        nonlocal count
        proxy = random.choice(proxies) if proxies else None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if loop.run_until_complete(send_view(url, proxy)):
            with lock:
                count += 1
                print(f"[+] View #{count}/{target} added via {proxy or 'direct'}")
        else:
            print(f"[-] Failed to send view using proxy {proxy or 'direct'}")

    threads = []
    while count < target:
        # Create a burst of threads
        for _ in range(min(10, target - count)):  # Reduced thread count for browser automation
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Wait for all threads in the burst to complete
        for t in threads:
            t.join()

        threads = []
        # Pause between bursts
        time.sleep(random.uniform(5, 10))

    print(f"\n[+] All {target} views have been dispatched.")
    print("Please allow 5-10 minutes for the view count to update due to TikTok's caching.")

if __name__ == "__main__":
    main()
