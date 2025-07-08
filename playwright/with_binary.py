import os
import subprocess
import time
from playwright.sync_api import sync_playwright

def main():
    # Get the current directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the start.sh script
    start_script_path = os.path.join(current_dir, "start.sh")
    
    # Chrome launch arguments for start.sh
    profile_name = "scytherkalachuchi"
    debug_port = "9222"
    headless = "false"  # Set to "true" for headless mode
    
    print(f"Launching Chrome via start.sh with profile: {profile_name}, port: {debug_port}")
    
    # Launch Chrome using the bash script
    chrome_process = subprocess.Popen([
        "bash", 
        start_script_path, 
        profile_name, 
        debug_port, 
        headless
    ])
    
    # Wait a bit for Chrome to start up
    time.sleep(10)
    
    print(f"Chrome launched with debug port {debug_port}")
    print(f"You can connect to chrome://inspect or http://localhost:{debug_port}")
    
    try:
        with sync_playwright() as p:
            # Connect to the existing Chrome instance via CDP
            browser = p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            print("Connected to Chrome via CDP")
            
            # Get the default context (or create a new one)
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
            else:
                context = browser.new_context()
            
            # Create a new page
            page = context.new_page()
             
            # pre screenshot
            

            page.screenshot(path=os.path.join(current_dir, "screenshot1.png"))

            # # Set a realistic user agent
            # page.set_extra_http_headers({
            #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            # # })
            
            # Navigate to a website
            page.goto("https://chatgpt.com")
            
            page.wait_for_load_state('networkidle')

            # Example: Take a screenshot
            screenshot_path = os.path.join(current_dir, "screenshot2.png")
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            
            # Example: Get page title
            title = page.title()
            print(f"Page title: {title}")
            
            # Keep the browser open for a while
            page.wait_for_timeout(5000)
            
            # Pause for interaction (optional)
            page.pause()
            
            # Disconnect from browser (but don't close it)
            browser.close()
            
    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
    
    finally:
        # Optionally terminate the Chrome process
        # Uncomment the next line if you want to close Chrome when script ends
        # chrome_process.terminate()
        print("Script finished. Chrome process is still running.")

if __name__ == "__main__":
    main()
