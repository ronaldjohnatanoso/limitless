import os
import subprocess
import time
import json
from playwright.sync_api import sync_playwright

def save_storage_state(context, storage_path):
    """Save the current browser storage state to a JSON file"""
    storage_state = context.storage_state()
    with open(storage_path, 'w') as f:
        json.dump(storage_state, f, indent=2)
    print(f"Storage state saved to: {storage_path}")

def load_storage_state(storage_path):
    """Load storage state from a JSON file"""
    if os.path.exists(storage_path):
        with open(storage_path, 'r') as f:
            return json.load(f)
    return None

def main():
    # Get the current directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the start.sh script
    start_script_path = os.path.join(current_dir, "start.sh")
    
    # Chrome launch arguments for start.sh
    profile_name = "n4"  # Change this for different profiles
    debug_port = "9222"
    headless = "false"  # Set to "true" for headless mode
    
    # Storage state file path
    storage_state_path = os.path.join(current_dir, f"storage_state_{profile_name}.json")
    
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
            
            # Load existing storage state if available
            storage_state = load_storage_state(storage_state_path)
            # Create context with or without storage state

            print("Creating new context (no existing storage state)")
            # Get the default context (or create a new one)
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
            else:
                context = browser.new_context()
            
            # Create a new page
            page = context.new_page()
             
            # Navigate to a website
            page.goto("https://chatgpt.com")
            
            page.wait_for_load_state('networkidle')

            # Take a screenshot
            screenshot_path = os.path.join(current_dir, f"screenshot_{profile_name}.png")
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            
            # Get page title
            title = page.title()
            print(f"Page title: {title}")
            
            # Keep the browser open for a while
            page.wait_for_timeout(5000)
            
            # Save current storage state before closing
            save_storage_state(context, storage_state_path)
            
            # Disconnect from browser (but don't close it)
            browser.close()
            
    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
    
    finally:
        print("Script finished. Chrome process is still running.")

if __name__ == "__main__":
    main()
