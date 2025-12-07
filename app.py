import streamlit as st
import time
import os
import subprocess
import json
import urllib.request
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Page Config ---
st.set_page_config(
    page_title="YouTube Ad Skipper",
    page_icon="📺",
    layout="wide"
)

# --- Session State Management ---
if "driver" not in st.session_state:
    st.session_state.driver = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "log_history" not in st.session_state:
    st.session_state.log_history = []

# --- Helper Functions ---

def log_msg(message):
    """Adds a message to the UI log."""
    timestamp = time.strftime('%H:%M:%S')
    st.session_state.log_history.insert(0, f"[{timestamp}] {message}")
    # Keep log history clean (last 50 lines)
    if len(st.session_state.log_history) > 50:
        st.session_state.log_history.pop()

def find_browser_executable(browser_choice):
    """Finds the path based on user selection."""
    paths = []
    if browser_choice == "Google Chrome":
        paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    elif browser_choice == "Brave":
        paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
    elif browser_choice == "Comet":
        paths = [
            "/Applications/Comet.app/Contents/MacOS/Comet",
            "/Applications/Comet Browser.app/Contents/MacOS/Comet Browser"
        ]
    
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def launch_browser_process(executable_path, profile_dir):
    """Launches the browser process in the background."""
    cmd = [
        executable_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-allow-origins=*"
    ]
    
    # Launch detached
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for port 9222
    placeholder = st.empty()
    for i in range(10):
        placeholder.info(f"Waiting for browser to launch... ({i+1}/10)")
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:9222/json/version") as url:
                if url.status == 200:
                    placeholder.empty()
                    return True
        except:
            pass
            
    placeholder.error("Could not detect browser on port 9222. Is it already running?")
    return False

def get_driver_connection(browser_choice, launch_mode):
    """Connects Selenium to the browser."""
    debug_profile_dir = os.path.expanduser("~/youtube_skipper_profile")
    if not os.path.exists(debug_profile_dir):
        os.makedirs(debug_profile_dir)

    # 1. Launch Logic
    if launch_mode == "Auto-Launch (Recommended)":
        exe_path = find_browser_executable(browser_choice)
        if not exe_path:
            st.error(f"Could not find executable for {browser_choice}")
            return None
        
        # Check if port is already open (browser running)
        is_open = False
        try:
            urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=1)
            is_open = True
            log_msg("Found existing browser instance on Port 9222.")
        except:
            pass

        if not is_open:
            log_msg(f"Launching {browser_choice}...")
            success = launch_browser_process(exe_path, debug_profile_dir)
            if not success:
                return None

    # 2. Version Detection
    target_version = None
    try:
        with urllib.request.urlopen("http://127.0.0.1:9222/json/version") as url:
            data = json.loads(url.read().decode())
            browser_string = data.get('Browser', '')
            match = re.search(r"Chrome/(\d+)\.", browser_string)
            if match:
                major_ver = int(match.group(1))
                if major_ver > 135:
                    log_msg(f"Detected Future Version {major_ver}. Using generic driver.")
                    target_version = None
                else:
                    target_version = match.group(0).split('/')[1]
    except Exception as e:
        log_msg(f"Version check warning: {e}")

    # 3. Install Driver
    try:
        if target_version:
            service = Service(ChromeDriverManager(driver_version=target_version).install())
        else:
            service = Service(ChromeDriverManager().install())
    except:
        service = Service(ChromeDriverManager().install())

    # 4. Attach
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"Could not attach to browser: {e}")
        return None

def fast_forward_ad(driver):
    """Speeds up video to 16x."""
    try:
        ad_active = driver.execute_script("""
            return (document.getElementsByClassName('ad-showing').length > 0) || 
                   (document.getElementsByClassName('ytp-ad-player-overlay').length > 0);
        """)
        if ad_active:
            driver.execute_script("""
                var videos = document.querySelectorAll('video');
                videos.forEach(video => {
                    video.muted = true;
                    video.playbackRate = 16.0;
                });
            """)
            return True
    except:
        pass
    return False

def ensure_youtube_tab(driver):
    """Switches focus to YouTube tab."""
    try:
        if "YouTube" in driver.title:
            return
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "YouTube" in driver.title:
                return
    except:
        pass

# --- UI Layout ---

st.title("📺 YouTube Ad Skipper")
st.markdown("Automated ad skipping and fast-forwarding for Chrome/Comet.")

# Sidebar Config
with st.sidebar:
    st.header("Configuration")
    browser_choice = st.selectbox("Browser", ["Google Chrome", "Comet", "Brave"])
    launch_mode = st.radio(
        "Connection Mode", 
        ["Auto-Launch (Recommended)", "Manual Connect (Port 9222)"]
    )
    
    st.markdown("---")
    
    # Connect Button
    if st.button("🔌 Connect Browser", use_container_width=True):
        if st.session_state.driver is not None:
            try:
                st.session_state.driver.quit()
            except:
                pass
            st.session_state.driver = None
        
        driver = get_driver_connection(browser_choice, launch_mode)
        if driver:
            st.session_state.driver = driver
            log_msg("Browser Connected Successfully!")
            st.rerun()

    # Disconnect
    if st.session_state.driver:
        if st.button("❌ Disconnect", use_container_width=True):
            st.session_state.driver = None
            st.session_state.is_running = False
            st.rerun()

# Main Status Area
status_col, controls_col = st.columns([2, 1])

with status_col:
    if st.session_state.driver:
        st.success(f"✅ Connected to {browser_choice}")
        
        # Profile Info
        st.info("💡 **Tip:** If you are not logged in, sign in now. Your session is saved to `~/youtube_skipper_profile`.")
        
        if not st.session_state.is_running:
            if st.button("▶️ Start Monitoring", type="primary"):
                st.session_state.is_running = True
                st.rerun()
        else:
            st.warning("Running... (Press Stop to halt)")
            if st.button("⏹️ Stop Monitoring"):
                st.session_state.is_running = False
                st.rerun()
            
    else:
        st.warning("⚠️ Browser not connected. Use the sidebar to connect.")

# --- The Loop (Running Logic) ---
# In Streamlit, we put the loop in a container that updates
if st.session_state.is_running and st.session_state.driver:
    
    log_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # CSS Selectors
    SELECTORS = [
        ".ytp-skip-ad-button",       
        ".ytp-ad-skip-button",
        ".ytp-ad-skip-button-modern",
        "[id^='skip-button:']",      
        "//button[contains(@class, 'ytp-ad-skip-button')]"
    ]

    try:
        # We run a loop for a few seconds to process events, then rerun to keep UI responsive-ish
        # Or ideally, an infinite loop that breaks if the user clicks 'Stop' (which triggers rerun)
        
        with st.container():
            st.write("### 📜 Live Logs")
            log_display = st.empty()

        while st.session_state.is_running:
            driver = st.session_state.driver
            
            # 1. Update Logs in UI
            log_display.code("\n".join(st.session_state.log_history[:10]), language="text")
            
            try:
                # 2. Ensure Tab
                ensure_youtube_tab(driver)
                status_placeholder.text(f"Scanning... Active Tab: {driver.title[:30]}...")

                # 3. Skip Logic
                clicked = False
                for selector in SELECTORS:
                    try:
                        if selector.startswith("//"):
                            els = driver.find_elements(By.XPATH, selector)
                        else:
                            els = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for el in els:
                            if el.is_displayed():
                                driver.execute_script("arguments[0].click();", el)
                                log_msg("SKIP CLICKED!")
                                clicked = True
                                break
                    except:
                        pass
                    if clicked: break
                
                # 4. Fast Forward
                if not clicked:
                    if fast_forward_ad(driver):
                        # Don't log spam, just indication
                        pass
                
                time.sleep(1)
                
            except Exception as e:
                log_msg(f"Error in loop: {e}")
                st.session_state.is_running = False
                st.rerun()

    except Exception as e:
        st.error(f"Critical Error: {e}")
        st.session_state.is_running = False

elif not st.session_state.driver:
    st.markdown("""
    ### How to use:
    1. Select your browser in the **Sidebar**.
    2. Click **Connect Browser**.
    3. Once connected, click **Start Monitoring**.
    4. You can minimize this window, but **do not close it**.
    """)