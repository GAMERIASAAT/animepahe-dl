
"""
This module provides utility functions for the AnimePahe Downloader.
"""

import json
import os

import urllib3


def is_termux() -> bool:
    """
    Detects whether the application is running inside Termux on Android.

    Returns:
        True if a Termux environment is detected, otherwise False.
    """
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix or os.path.isdir("/data/data/com.termux")


def normalize_base_url(url: str) -> str:
    """
    Normalizes a user-supplied base URL for the AnimePahe site/mirror.

    Ensures the URL has a scheme (defaults to ``https://``) and strips any
    trailing slash so it can be concatenated with API paths safely.

    Args:
        url: The raw base URL entered by the user (e.g. ``animepahe.ru``).

    Returns:
        A normalized base URL (e.g. ``https://animepahe.ru``).
    """
    url = (url or "").strip()
    if not url:
        return url
    if "://" not in url:
        url = f"https://{url}"
    return url.rstrip("/")


def notify(title: str, message: str, timeout: int = 10) -> bool:
    """
    Sends a desktop notification if a backend is available.

    Notifications are best-effort: on headless or terminal-only environments
    (such as Termux) the ``plyer`` backend may be missing or unable to display
    anything. In those cases this function fails silently and returns False
    instead of raising.

    Args:
        title: The notification title.
        message: The notification body.
        timeout: How long the notification should remain visible, in seconds.

    Returns:
        True if a notification was dispatched, otherwise False.
    """
    try:
        from plyer import notification as _notification

        _notification.notify(
            title=title,
            message=message,
            app_name="Animepahe Downloader",
            timeout=timeout,
        )
        return True
    except Exception:
        # plyer not installed, or no usable notification backend on this platform.
        return False


def sanitize_filename(name: str) -> str:
    """
    Sanitizes a string to be used as a valid file or folder name.

    Args:
        name: The string to sanitize.

    Returns:
        The sanitized string.
    """
    name = name.lstrip(".")
    # Remove invalid characters for Windows filenames
    invalid_chars = '<>/\\|:\"*?'
    for char in invalid_chars:
        name = name.replace(char, '')
    return "".join(c for c in name if c.isalnum() or c in " .-_()").rstrip()

def get_airing_anime():
    """
    Fetches the currently airing anime from AnimePahe.

    Returns:
        A dictionary containing the airing anime data, or None if the request fails.
    """
    try:
        http = urllib3.PoolManager(10, headers={"Referer": "https://kwik.cx/", "Accept": "","Connection": "Keep-Alive","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US,en;q=0.9","User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
        res = "https://animepahe.ru/api?m=airing&page1"
        r = http.request("GET", res, preload_content=False)
        return json.loads(r.data)
    except (urllib3.exceptions.MaxRetryError, json.JSONDecodeError) as e:
        print(f"Error fetching airing anime: {e}")
        return None
