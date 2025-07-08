import os
import subprocess
import time
import json
from playwright.sync_api import sync_playwright
import psutil

def load_storage_state(storage_path):
    """Load storage state from a JSON file"""
    if os.path.exists(storage_path):
        with open(storage_path, 'r') as f:
            return json.load(f)
    return None

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    start_script_path = os.path.join(current_dir, "start.sh")
    
    # Use a DIFFERENT profile name
    source_profile = "scytherkalachuchi"
    target_profile = "n4"
    debug_port = "9223"  # Different port
    headless = "false"
    
    # Load storage state from the source profile
    source_storage_path = os.path.join(current_dir, f"storage_state_{source_profile}.json")
    storage_state = load_storage_state(source_storage_path)
    
    if not storage_state:
        print(f"No storage state found at: {source_storage_path}")
        return
    
    print(f"Launching new Chrome profile: {target_profile}")
    
    # Launch Chrome with the new profile
    chrome_process = subprocess.Popen([
        "bash", 
        start_script_path, 
        target_profile, 
        debug_port, 
        headless
    ])
    
    time.sleep(10)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            print("Using existing default context and injecting storage...")
            # Get the existing default context instead of creating new one
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            
            # Manually inject cookies from storage state
            if storage_state and 'cookies' in storage_state:
                context.add_cookies(storage_state['cookies'])
                print(f"Injected {len(storage_state['cookies'])} cookies")
            
            # Get existing page or create new one
            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()
            
            # Inject localStorage and sessionStorage
            # if storage_state and 'origins' in storage_state:
            #     for origin_data in storage_state['origins']:
            #         origin_url = origin_data['origin']
                    
            #         # Navigate to the origin to set storage
            #         if page.url != origin_url:
            #             page.goto(origin_url)
                    
                    # # Inject localStorage with proper escaping
                    # if 'localStorage' in origin_data:
                    #     for item in origin_data['localStorage']:
                    #         page.evaluate("""
                    #             (args) => localStorage.setItem(args.name, args.value)
                    #         """, {"name": item['name'], "value": item['value']})
                    
                    # Inject sessionStorage with proper escaping
                    # if 'sessionStorage' in origin_data:
                    #     for item in origin_data['sessionStorage']:
                    #         page.evaluate("""
                    #             (args) => sessionStorage.setItem(args.name, args.value)
                    #         """, {"name": item['name'], "value": item['value']})
            
            # Navigate to final destination
            page.goto("https://chatgpt.com")
            page.wait_for_load_state('networkidle')
            
            screenshot_path = os.path.join(current_dir, f"loaded_storage_{target_profile}.png")
            page.screenshot(path=screenshot_path)
            print(f"Screenshot with loaded storage: {screenshot_path}")
            
            # page.pause()
            page.wait_for_timeout(5000)
            
            # Close browser INSIDE the Playwright context
            print("Closing browser...")
            for context in browser.contexts:
                context.close()
            browser.close()
            print("Browser closed gracefully")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Try graceful termination first
        try:
            print("Terminating Chrome process...")
            chrome_process.terminate()
            chrome_process.wait(timeout=3)
            print("Chrome process terminated successfully")
        except subprocess.TimeoutExpired:
            print("Chrome didn't terminate gracefully, force killing...")
            chrome_process.kill()
            chrome_process.wait()
        
        # Force kill any remaining Chrome processes on this port
        try:
            subprocess.run([
                "pkill", "-f", f"remote-debugging-port={debug_port}"
            ], timeout=5)
            print("Force killed Chrome processes")
        except Exception as e:
            print(f"Error force killing Chrome: {e}")
        
        # Wait a moment for processes to clean up
        time.sleep(1)

if __name__ == "__main__":
    main()