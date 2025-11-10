import tls_client
import random
import time
import threading
import re
from urllib.parse import urlparse

def extract_video_info(url):
    """
    Resolves a TikTok URL (including short links) and extracts the username and video ID.
    """
    session = tls_client.Session(client_identifier="chrome_120")
    try:
        # Follow redirects to get the final URL, which contains the needed info
        response = session.get(url, allow_redirects=True, timeout_seconds=15)
        final_url = response.url

        # Regex to find username and video ID from the full URL
        match = re.search(r'@(?P<username>[^/]+)/video/(?P<aweme_id>\d+)', final_url)
        if match:
            return match.group('username'), match.group('aweme_id')
    except Exception as e:
        print(f"An error occurred while resolving the URL: {e}")

    return None, None

def get_video_embed_url(username, aweme_id):
    """
    Constructs the video embed URL using the extracted username and video ID.
    """
    return f"https://www.tiktok.com/@{username}/video/{aweme_id}"

def get_ua():
    """
    Returns a random user-agent string.
    """
    uas = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36"
    ]
    return random.choice(uas)

def get_proxies():
    """
    Returns a list of proxies.
    IMPORTANT: The user must replace the placeholder proxies below with their own.
    """
    # Replace with your residential proxies (e.g., from BrightData API)
    return ["http://user:pass@proxy1.brightdata.com:22225", "http://user:pass@proxy2.brightdata.com:22225"]

def send_view(username, aweme_id, proxy=None):
    """
    Sends a view to the specified video.
    """
    session = tls_client.Session(client_identifier="chrome_120") # Mimics Chrome TLS
    session.headers.update({
        "User-Agent": get_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    embed_url = get_video_embed_url(username, aweme_id)
    try:
        resp = session.get(embed_url, timeout_seconds=15)
        if resp.status_code == 200 and "aweme_id" in resp.text:
            # Simulate watch time
            time.sleep(random.uniform(3, 7))
            # Optional: Hit stats endpoint
            stats_url = f"https://m.tiktok.com/aweme/v1/aweme/stats/?aweme_id={aweme_id}"
            session.get(stats_url, timeout_seconds=15)
            return True
    except Exception:
        pass
    return False

def main():
    url = input("Enter TikTok video URL: ").strip()
    username, aweme_id = extract_video_info(url)
    if not username or not aweme_id:
        print("Invalid or unsupported URL!")
        return

    try:
        target = int(input("How many views: "))
    except ValueError:
        print("Invalid number of views.")
        return

    proxies = get_proxies()

    lock = threading.Lock()
    count = 0

    def worker():
        nonlocal count
        proxy = random.choice(proxies) if proxies else None
        if send_view(username, aweme_id, proxy):
            with lock:
                count += 1
                print(f"[+] View #{count}/{target} added via {proxy or 'direct'}")

    threads = []
    while count < target:
        # Create a burst of threads
        for _ in range(min(20, target - count)):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Wait for all threads in the burst to complete
        for t in threads:
            t.join()

        threads = []
        # Pause between bursts
        time.sleep(random.uniform(10, 20))

    print(f"\n[+] All {target} views have been dispatched.")
    print("Please allow 5-10 minutes for the view count to update due to TikTok's caching.")

if __name__ == "__main__":
    main()
