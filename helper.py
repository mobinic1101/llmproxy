import webbrowser


def open_captcha_browser(url: str) -> bool:
    """Open the operating system's default browser at the captcha form URL.

    The user solves the CAPTCHA in the opened browser and submits the answer
    through /captcha-answer.
    """
    print(f"Opening captcha form in browser: {url}")
    return webbrowser.open(url, new=2, autoraise=True)
