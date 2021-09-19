import music
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from http import server

running = False

KEEP_RUNNING = True


class S(server.BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global KEEP_RUNNING
        self._set_response()
        self.wfile.write("GET request for {}".format(
            self.path).encode('utf-8'))
        KEEP_RUNNING = False


def keep_running():
    return KEEP_RUNNING


def run(server_class=server.HTTPServer, handler_class=S):
    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    while keep_running():
        httpd.handle_request()
    run_bot()


def run_bot():
    cogs = [music]

    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    for i in range(len(cogs)):
        cogs[i].setup(client)

    client.run(os.getenv('DISCORD_BOT_TOKEN'))


if __name__ == '__main__':

    load_dotenv()
    run()
