
<div align="center">

# 📺✨ SkipAd  
### *Automated YouTube Ad Skipping & 16× Fast-Forwarding Tool*


<img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge">
<img src="https://img.shields.io/badge/Selenium-Automation-green?style=for-the-badge">
<img src="https://img.shields.io/badge/Mac%20M1%2FM2-Optimized-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/License-Educational-lightgrey?style=for-the-badge">


### 🚀 Skip ads instantly. Fast-forward unskippable ads. Stay logged in forever.
**Supports Chrome • Brave • Comet (Perplexity Browser)**

</div>

---

## 👨‍💻 Developer Details

**Ram Bikkina** || **Python Dev** - Building AI Agents || [Know Me At](https://ramc26.github.io/RamTechSuite)

---

## ✨ Features

✔ **Auto-Skip Ads** – Instantly clicks *Skip Ad* when it appears  
✔ **Fast-Forward Unskippable Ads (16×)** – Mutes and speeds ads to 1600%  
✔ **Persistent Login Mode** – Keeps YouTube signed in  
✔ **Supports Chrome, Brave & Comet**  
✔ **Smart Driver Detection** – Handles browser version mismatches  
✔ **Apple Silicon Optimized** – Works flawlessly on M1/M2  

---

## 🛠️ Prerequisites

You need:

- Python 3.10+
- **uv** (super fast Python package manager)

### Install uv

#### macOS / Linux
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
````

#### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart terminal after installation ✔️

---

## 🚀 Installation

### Clone the repo

```sh
git clone https://github.com/Ramc26/SkipAd.git
cd SkipAd
```

### Install dependencies

```sh
uv sync
```

---

## ▶️ Usage
### 🖥️ Choose How to Run the YouTube Ad Skipper

Now you can use the tool in **two ways**:

* **🎛️ Streamlit Web UI (Beginner-friendly)**
* **🖥️ Terminal / CLI Mode (Power users)**

Both modes provide the same features — auto-skip, fast-forwarding ads, and persistent login.

---

# 🎛️ Streamlit Web UI Mode (Recommended)

A clean graphical interface to connect your browser, start/stop monitoring, and view real-time logs.

## ▶️ Run the Streamlit App

From the project root:

```sh
uv run streamlit run app.py
```

This opens a beautiful UI at:

```
http://localhost:8501
```

---

## 🧭 Features in the UI

### 🔌 Connect to Browser

Choose your browser:

* Google Chrome
* Brave
* Comet (Perplexity)

Choose connection mode:

* **Auto-Launch (Recommended)**
* **Manual Connect to Port 9222**

---

### ▶️ Start / Stop Monitoring

Click:

* **Start Monitoring** → begins ad scanning
* **Stop Monitoring** → halts instantly

---

### 📜 Live Logs Panel

Shows:

* Skip button clicks
* Fast-forward activations
* Errors or warnings
* Browser connection status

---

### 💡 Persistent Login

The UI also uses:

```
~/youtube_skipper_profile
```

Meaning: **You only log in to YouTube once.**

---

# 🧠 Streamlit Architecture (Internal)

The UI uses:

* **Selenium WebDriver** (attached to existing Chrome/Comet instance)
* **Streamlit Session State** to manage driver object & loop
* **Real-time log history display**
* **Graceful stop mechanism** via rerun()

---

# 🖥️ Terminal (CLI) Mode

If you prefer coding tools, automation scripts, or no UI, use the classic mode:

```sh
uv run main.py
```

You will see the menu:

1. Google Chrome (New Window)
2. Brave Browser (New Window)
3. Comet (New Window)
4. **CONNECT TO RUNNING BROWSER** (Persistent Login)

Choose your option and proceed exactly as before.

---

# 📌 Browser Launch Command (For both UI & CLI)

### Chrome

```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
--remote-debugging-port=9222 \
--user-data-dir="$HOME/youtube_skipper_profile"
```

### Comet

```sh
/Applications/Comet.app/Contents/MacOS/Comet \
--remote-debugging-port=9222 \
--user-data-dir="$HOME/youtube_skipper_profile"
```

---

# 🧭 Folder Structure (Updated)

```
SkipAd/
├── main.py           # Terminal/CLI version
├── app.py            # Streamlit UI version
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 🤝 Which mode should you use?

| Mode              | Best For               | Pros                                 |
| ----------------- | ---------------------- | ------------------------------------ |
| **Streamlit UI**  | Beginners, daily usage | No terminal required, real-time logs |
| **Terminal Mode** | Developers, automation | Faster, scriptable                   |

---

## ⚠️ Troubleshooting

| Issue                    | Fix                                                  |
| ------------------------ | ---------------------------------------------------- |
| **Connection Refused**   | You didn’t launch Chrome/Comet with remote debugging |
| **Session Not Created**  | Fully close browser before using Options 1–3         |
| **Driver Version Error** | Auto-fixed — script falls back to stable version     |

---

## 📝 License

This project is for **educational & personal automation purposes** only.

### Suggestions & Bugs
If you find any issues or have ideas to improve the project, feel free to reach out or open an issue.

**GitHub Issues:** https://github.com/Ramc26/SkipAd/issues  
**Developer:** Ram Bikkina — https://ramc26.github.io/RamTechSuite

<div align="center">

## 💡 Created by **🦉 Ram Bikkina**
<img src="https://img.shields.io/badge/Thanks%20for%20Visiting!-white?style=for-the-badge">

</div>