import sys
import yt_dlp

def analyze_video(video_url):
    """
    Analyzes a TikTok video and prints its metadata using yt-dlp.
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            print("Video Analysis:")
            print(f"  - Uploader: {info_dict.get('uploader')}")
            print(f"  - Title: {info_dict.get('title')}")
            print(f"  - Description: {info_dict.get('description')}")
            print(f"  - Likes: {info_dict.get('like_count')}")
            print(f"  - Comments: {info_dict.get('comment_count')}")
            print(f"  - Views: {info_dict.get('view_count')}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        analyze_video(video_url)
    else:
        print("Please provide a TikTok video URL as a command-line argument.")
