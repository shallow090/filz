import asyncio
import logging
import glob
import importlib
import sys
from pathlib import Path
from aiohttp import web
from pyrogram import Client, idle

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

from config import LOG_CHANNEL, CLONE_MODE
from plugins.clone import restart_bots

ppath = "plugins/*.py"
files = glob.glob(ppath)

async def start_bot():
    print('\n')
    print('Initalizing Horizon Bot')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Bot Imported => " + plugin_name)

    if CLONE_MODE:
        await restart_bots()
    print("Bot Started Powered By @Horizon_Bots")
    await idle()

async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

async def main():
    await asyncio.gather(start_bot(), start_web_server())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
