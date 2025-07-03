from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Using system Chrome for better stealth
        browser = p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",  # Update this path
            args=[
                "--no-first-run",
                "--no-default-browser-check", 
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Hide automation indicators
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        page = context.new_page()
        page.goto("https://example.com")
        
        print("Browser opened. Press Enter to close...")
        input()
        
        browser.close()

if __name__ == "__main__":
    main()