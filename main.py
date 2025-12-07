import time
import os
import sys
import json
import urllib.request
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_browser_choice():
    print("\n--- YouTube Ad Skipper ---")
    print("1. Google Chrome (New Window)")
    print("2. Brave Browser (New Window)")
    print("3. Comet (Launch New Window)")
    print("4. ** CONNECT TO RUNNING BROWSER ** (Recommended)")
    print("   (Keeps you signed in, prevents crashes)")
    choice = input("Select your browser (1-4): ")
    return choice

def get_driver(choice):
    # Create a persistent folder in your home directory for this script
    # This ensures your login is SAVED every time you run this.
    debug_profile_dir = os.path.expanduser("~/youtube_skipper_profile")
    
    # --- OPTION 4: ATTACH TO RUNNING BROWSER ---
    if choice == '4':
        print("\n--- INSTRUCTIONS ---")
        print("1. Close your browser completely (Cmd+Q).")
        print("2. Copy and Run this EXACT command in Terminal:")
        
        print("\n   FOR CHROME:")
        print(f'   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="{debug_profile_dir}"')
        
        print("\n   FOR COMET:")
        print(f'   /Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222 --user-data-dir="{debug_profile_dir}"')
        
        print("\n3. The browser will open as 'Guest' the first time.")
        print("   -> SIGN IN to YouTube manually now.")
        print("   -> Next time you run this command, you will still be signed in!")
        
        input("\nPress ENTER here once the browser is running...")
        print("Connecting to browser...")

        # STEP 1: Version Detection
        target_version = None
        try:
            with urllib.request.urlopen("http://127.0.0.1:9222/json/version") as url:
                data = json.loads(url.read().decode())
                browser_string = data.get('Browser', '')
                print(f"Found Engine: {browser_string}")
                
                match = re.search(r"Chrome/(\d+)\.", browser_string)
                if match:
                    major_ver = int(match.group(1))
                    if major_ver > 135:
                        # Fix for Comet reporting future versions
                        target_version = None 
                    else:
                        target_version = match.group(0).split('/')[1]
        except Exception as e:
            print(f"Waiting for connection... (Ensure you ran the command above!)")
            print(f"Error details: {e}")

        # STEP 2: Install Driver
        try:
            if target_version:
                service = Service(ChromeDriverManager(driver_version=target_version).install())
            else:
                service = Service(ChromeDriverManager().install())
        except Exception as e:
            service = Service(ChromeDriverManager().install())

        # STEP 3: Connect
        attach_options = Options()
        attach_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        attach_options.add_argument("--remote-allow-origins=*")
        
        try:
            driver = webdriver.Chrome(service=service, options=attach_options)
            return driver
        except Exception as e:
            print(f"\nCould not attach: {e}")
            return None

    # --- OPTIONS 1-3: LAUNCH NEW BROWSER ---
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    binary_path = None

    if choice == '1':
        print("Launching Chrome...")
    elif choice == '2':
        print("Configuring for Brave...")
        potential_paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
        for path in potential_paths:
            if os.path.exists(path):
                binary_path = path; break
    elif choice == '3':
        print("Configuring for Comet...")
        potential_paths = [
            "/Applications/Comet.app/Contents/MacOS/Comet",
            "/Applications/Comet Browser.app/Contents/MacOS/Comet Browser",
        ]
        for path in potential_paths:
            if os.path.exists(path):
                binary_path = path; break
        
        if not binary_path:
            binary_path = input("Paste Comet path: ").strip('"')

    if binary_path:
        options.binary_location = binary_path
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")

    if choice in ['1', '2', '3']:
        # Use the same persistent folder for launch mode too
        print(f"Using persistent profile at: {debug_profile_dir}")
        options.add_argument(f"--user-data-dir={debug_profile_dir}")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error: {e}")
        return None

def fast_forward_ad(driver):
    """
    If an ad is playing but unskippable, this mutes it and speeds it up to 16x.
    """
    try:
        # Check if an ad is actually showing
        ad_showing = driver.execute_script(
            "return document.getElementsByClassName('ad-showing').length > 0;"
        )
        
        if ad_showing:
            # Targeted script for the main HTML5 video player
            driver.execute_script("""
                var video = document.querySelector('.html5-main-video');
                if (video) {
                    video.muted = true;
                    video.playbackRate = 16.0;
                }
            """)
            return True
    except:
        pass
    return False

def main():
    choice = get_browser_choice()
    driver = get_driver(choice)
    
    if not driver:
        return

    print("\nBrowser Connected Successfully!")
    if choice != '4':
        print("Navigating to YouTube...")
        driver.get("https://www.youtube.com")
    
    print("\n--- Background Monitor Running ---")
    print("Watching for Ads (Skipping or Fast-Forwarding)...")
    print("Press Ctrl+C to stop.")

    SKIP_BUTTON_SELECTORS = [
        ".ytp-skip-ad-button",       
        ".ytp-ad-skip-button",       
        "[id^='skip-button:']",      
        ".ytp-skip-ad-button__text"  
    ]

    try:
        while True:
            clicked = False
            
            # 1. Try to click Skip Button
            for selector in SKIP_BUTTON_SELECTORS:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        element.click()
                        print(f"[{time.strftime('%H:%M:%S')}] Ad Skipped (Clicked)!")
                        clicked = True
                        time.sleep(1)
                        break 
                except:
                    pass
            
            # 2. If no button clicked, try Fast Forwarding unskippable ads
            if not clicked:
                if fast_forward_ad(driver):
                    pass

            time.sleep(1) # Check every second

    except KeyboardInterrupt:
        print("\nStopping script...")
        if choice != '4':
            driver.quit()
        else:
            print("Detached from browser.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()


# import time
# import os
# import sys
# import subprocess
# import json
# import urllib.request
# import re
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# def get_browser_choice():
#     print("\n--- YouTube Ad Skipper ---")
#     print("This mode launches a separate 'Bot Browser' that saves your login.")
#     print("1. Google Chrome (Recommended)")
#     print("2. Brave Browser")
#     print("3. Comet")
#     choice = input("Select your browser (1-3): ")
#     return choice

# def find_browser_executable(choice):
#     paths = []
#     if choice == '1': # Chrome
#         paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
#     elif choice == '2': # Brave
#         paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
#     elif choice == '3': # Comet
#         paths = [
#             "/Applications/Comet.app/Contents/MacOS/Comet",
#             "/Applications/Comet Browser.app/Contents/MacOS/Comet Browser"
#         ]
    
#     for p in paths:
#         if os.path.exists(p):
#             return p
            
#     print(f"Could not find browser for selection {choice}.")
#     custom = input("Paste the full path to the executable: ").strip().strip('"')
#     return custom

# def launch_browser_process(executable_path, profile_dir):
#     print(f"\nLaunching browser from: {executable_path}")
#     print(f"Using Profile: {profile_dir}")
    
#     cmd = [
#         executable_path,
#         "--remote-debugging-port=9222",
#         f"--user-data-dir={profile_dir}",
#         "--no-first-run",
#         "--no-default-browser-check",
#         "--remote-allow-origins=*" 
#     ]
    
#     subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
#     print("Waiting for browser to initialize...")
#     for i in range(10):
#         time.sleep(1)
#         try:
#             with urllib.request.urlopen("http://127.0.0.1:9222/json/version") as url:
#                 if url.status == 200:
#                     print("Browser Port 9222 is open!")
#                     return True
#         except:
#             pass
    
#     print("Warning: Could not detect open port 9222. Attempting to connect anyway...")
#     return False

# def get_driver(choice):
#     debug_profile_dir = os.path.expanduser("~/youtube_skipper_profile")
#     if not os.path.exists(debug_profile_dir):
#         os.makedirs(debug_profile_dir)

#     exe_path = find_browser_executable(choice)
#     if not exe_path or not os.path.exists(exe_path):
#         print("Invalid browser path.")
#         return None

#     # Launch
#     launch_browser_process(exe_path, debug_profile_dir)

#     # Detect Version
#     target_version = None
#     try:
#         with urllib.request.urlopen("http://127.0.0.1:9222/json/version") as url:
#             data = json.loads(url.read().decode())
#             browser_string = data.get('Browser', '')
#             print(f"Engine Detected: {browser_string}")
            
#             match = re.search(r"Chrome/(\d+)\.", browser_string)
#             if match:
#                 major_ver = int(match.group(1))
#                 if major_ver > 135:
#                     print(f"Note: High version ({major_ver}) detected. Using standard driver.")
#                     target_version = None 
#                 else:
#                     target_version = match.group(0).split('/')[1]
#     except Exception as e:
#         print(f"Version check failed: {e}")

#     # Install Driver
#     try:
#         if target_version:
#             service = Service(ChromeDriverManager(driver_version=target_version).install())
#         else:
#             service = Service(ChromeDriverManager().install())
#     except Exception as e:
#         print(f"Driver download error: {e}. Trying fallback...")
#         service = Service(ChromeDriverManager().install())

#     # Connect
#     print("Attaching Selenium to port 9222...")
#     attach_options = Options()
#     attach_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
#     try:
#         driver = webdriver.Chrome(service=service, options=attach_options)
#         return driver
#     except Exception as e:
#         print(f"\nCould not attach: {e}")
#         return None

# def ensure_youtube_tab(driver):
#     """
#     Scans all open tabs and switches focus to the one playing YouTube.
#     """
#     try:
#         current_handle = driver.current_window_handle
#         current_title = driver.title
        
#         # If we are already on YouTube, return
#         if "YouTube" in current_title:
#             return True

#         # Loop through all tabs to find YouTube
#         for handle in driver.window_handles:
#             driver.switch_to.window(handle)
#             if "YouTube" in driver.title:
#                 print(f"Switched focus to tab: {driver.title}")
#                 return True
        
#         # If not found, switch back to original (or keep searching next loop)
#         driver.switch_to.window(current_handle)
#     except Exception as e:
#         pass
#     return False

# def fast_forward_ad(driver):
#     """
#     Speeds up ANY video element found on the page.
#     """
#     try:
#         # Check for ad indicator class OR if skip button is present but not clickable yet
#         ad_active = driver.execute_script("""
#             return (document.getElementsByClassName('ad-showing').length > 0) || 
#                    (document.getElementsByClassName('ytp-ad-player-overlay').length > 0);
#         """)
        
#         if ad_active:
#             # Force speed up on ALL video tags (aggressive)
#             driver.execute_script("""
#                 var videos = document.querySelectorAll('video');
#                 videos.forEach(video => {
#                     video.muted = true;
#                     video.playbackRate = 16.0;
#                 });
#             """)
#             return True
#     except:
#         pass
#     return False

# def main():
#     print("Make sure your browser is CLOSED before starting.")
#     choice = get_browser_choice()
#     driver = get_driver(choice)
    
#     if not driver:
#         print("Failed to start. Exiting.")
#         return

#     print("\nSUCCESS: Browser Connected!")
#     print("--- Ad Skipper Running ---")
#     print("Watching for Ads (Skipping or Fast-Forwarding)...")
#     print("Press Ctrl+C to stop.")

#     # Selectors for the button itself
#     SKIP_BUTTON_SELECTORS = [
#         ".ytp-skip-ad-button",       
#         ".ytp-ad-skip-button",
#         ".ytp-ad-skip-button-modern",
#         "[id^='skip-button:']",      
#         ".ytp-skip-ad-button__text",
#         "//button[contains(@class, 'ytp-ad-skip-button')]" # XPath fallback
#     ]

#     try:
#         while True:
#             # 1. Ensure we are looking at the right tab
#             ensure_youtube_tab(driver)
            
#             clicked = False
            
#             # 2. Try to click Skip Button
#             for selector in SKIP_BUTTON_SELECTORS:
#                 try:
#                     if selector.startswith("//"):
#                         element = driver.find_element(By.XPATH, selector)
#                     else:
#                         element = driver.find_element(By.CSS_SELECTOR, selector)
                    
#                     if element and element.is_displayed():
#                         # Use JavaScript Click (Hard Click)
#                         driver.execute_script("arguments[0].click();", element)
#                         print(f"[{time.strftime('%H:%M:%S')}] Ad Skipped (Clicked)!")
#                         clicked = True
#                         time.sleep(0.5)
#                         break 
#                 except:
#                     pass
            
#             # 3. If no button clicked, try Fast Forwarding unskippable ads
#             if not clicked:
#                 if fast_forward_ad(driver):
#                     # Quietly speeding up
#                     pass

#             time.sleep(1)

#     except KeyboardInterrupt:
#         print("\nStopping script...")
#         print("Browser left open. Bye!")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     main()