import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import bot  # Import the bot module

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print(f"----- SYSTEM INFO -----")
    print(f"Python Version: {sys.version}")
    print(f"-----------------------")
    # Start the bot as a background task
    asyncio.create_task(bot.start_bot())
    bot.logger.info("Web Dashboard Started")
    yield
    # Shutdown logic
    await bot.stop_bot()

app = FastAPI(title="Hinata Bot Dashboard", lifespan=lifespan)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ControlAction(BaseModel):
    action: str

class BroadcastMsg(BaseModel):
    target: str
    message: str



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def get_data():
    """Returns all users and groups with full metadata."""
    users = bot.read_json("users.json", [])
    groups = bot.read_json("groups.json", [])
    
    # Ensure backward compatibility/formatting
    formatted_users = []
    for u in users:
        if isinstance(u, dict): formatted_users.append(u)
        else: formatted_users.append({"id": u, "name": "Legacy User", "username": "unknown"})
        
    formatted_groups = []
    for g in groups:
        if isinstance(g, dict): formatted_groups.append(g)
        else: formatted_groups.append({"id": g, "title": "Legacy Group"})

    return {
        "stats": {
            "users_count": len(users),
            "groups_count": len(groups),
            "broadcasts": bot.STATS.get("broadcasts", 0),
            "uptime": bot.get_uptime(),
            "status": bot.STATS.get("status", "online"),
            "global_access": bot.CONFIG.get("global_access", True)
        },
        "users": formatted_users,
        "groups": formatted_groups,
        "banned_users": bot.CONFIG.get("banned_users", [])
    }


@app.get("/api/logs")
async def get_logs():
    # Read last 50 lines from log file
    if os.path.exists(bot.LOG_FILE):
        with open(bot.LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-50:]
    return ["Log file not found."]

@app.post("/api/control")
async def control_bot(data: ControlAction):
    if data.action == "restart":
        await bot.stop_bot()
        asyncio.create_task(bot.start_bot())
        return {"success": True}
    elif data.action == "clear_logs":
        if os.path.exists(bot.LOG_FILE):
            open(bot.LOG_FILE, "w").close()
        return {"success": True}
    elif data.action == "toggle_access":
        bot.CONFIG["global_access"] = not bot.CONFIG.get("global_access", True)
        bot.save_config(bot.CONFIG)
        return {"success": True, "new_status": bot.CONFIG["global_access"]}
    elif data.action == "delete_broadcast":
        history = bot.read_json("broadcast_history.json", [])
        if not history:
            return {"success": False, "error": "No broadcast history found"}
        
        s = f = 0
        if not bot.app:
            return {"success": False, "error": "Bot not initialized"}
            
        for entry in history:
            try:
                await bot.app.bot.delete_message(chat_id=entry['chat_id'], message_id=entry['message_id'])
                s += 1
            except:
                f += 1
        
        bot.write_json("broadcast_history.json", [])
        return {"success": True, "deleted": s, "failed": f}
    elif data.action == "toggle_bot":
        if bot.STATS.get("status") == "online":
            await bot.stop_bot()
        else:
            asyncio.create_task(bot.start_bot())
        return {"success": True}
    return {"success": False, "error": "Unknown action"}

@app.post("/api/broadcast")
async def api_broadcast(data: BroadcastMsg):
    try:
        if not bot.app:
            return {"success": False, "error": "Bot not initialized"}
        
        count = 0
        s_users = f_users = s_groups = f_groups = 0
        if data.target == "all" or data.target == "users":
            users = bot.read_json("users.json", [])
            for u in users:
                uid = u.get('id') if isinstance(u, dict) else u
                try: 
                    sent = await bot.app.bot.send_message(chat_id=uid, text=data.message)
                    bot.save_broadcast_msg(sent.chat_id, sent.message_id)
                    s_users += 1
                except:
                    f_users += 1
        
        if data.target == "all" or data.target == "groups":
            groups = bot.read_json("groups.json", [])
            for g in groups:
                gid = g.get('id') if isinstance(g, dict) else g
                try: 
                    sent = await bot.app.bot.send_message(chat_id=gid, text=data.message)
                    bot.save_broadcast_msg(sent.chat_id, sent.message_id)
                    s_groups += 1
                except:
                    f_groups += 1
                
        bot.update_stats(s_users, f_users, s_groups, f_groups)
        bot.STATS["broadcasts"] = bot.STATS.get("broadcasts", 0) + 1
        return {"success": True, "sent_count": s_users + s_groups}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Use environment variables for port (Render uses PORT env)
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
