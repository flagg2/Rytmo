import music
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from http import server


class S(server.BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(
            self.path).encode('utf-8'))


def run(server_class=server.HTTPServer, handler_class=S):
    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


load_dotenv()
run()

cogs = [music]


client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run(os.getenv('DISCORD_BOT_TOKEN'))
