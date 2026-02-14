# 🚀 Deploying Hinata Bot v2.5 with Web Dashboard

Your bot now features a **Premium Web Control Panel** with real-time logs, stats, and broadcast controls!

## 1. Prerequisites

- A **GitHub** account.
- A **Render.com** account.
- Your Telegram **Bot Token** (from @BotFather).

## 2. Project Structure Changes

- `main.py`: The entry point for FastAPI and the Bot.
- `static/`: Contains the CSS and JS for the dashboard.
- `templates/`: Contains the HTML for the dashboard.
- `requirements.txt`: Now includes `fastapi` and `uvicorn`.

## 3. Deployment Steps

### Step A: Push to GitHub

1. Upload all files to a new GitHub repository.
2. Ensure `token.txt` contains your bot token (or set it as an Environment Variable in the future).

### Step B: Setup on Render

1. Log in to [Render.com](https://render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Set the following configurations:
   - **Name**: `hinata-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. **IMPORTANT (Fixes common errors):**
   - Go to **Settings** -> **Environment Variables**.
   - Add a new variable: `PYTHON_VERSION` with value `3.11.10`.
   - This ensures Render doesn't use experimental versions like 3.14.
6. Click **Create Web Service**.

## 4. Accessing Your Dashboard

Once deployed, Render will provide a URL like `https://hinata-bot.onrender.com`.

- Open this URL in your browser to access the **Control Panel**.
- You can monitor uptime, users, and send broadcats directly from the web!

## 5. Environment Variables (Recommended)

Instead of `token.txt`, you can add a secret file or environment variable on Render for better security.

---

**Note**: Render's free tier spins down after 15 minutes of inactivity. The dashboard will automatically keep the bot alive as long as there is traffic or if you use a "Ping" service.
