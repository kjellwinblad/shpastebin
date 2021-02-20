#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Kjell Winblad
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from urllib.parse import parse_qs
from cgi import parse_header, parse_multipart
import argparse

pastes_dir = os.path.join(os.path.dirname(__file__), 'pastes')

def create_if_not_existing(path):
    if not os.path.isfile(path):
        with open(path, "w") as file:
            file.write("")

def get_file_content(path):
    with open(path, "r") as file:
        return file.read()

def write_file_content(path, content):
    with open(path, "w") as file:
        return file.write(content)

def get_paste_path(url_path_part):
    filename = url_path_part[1:] if url_path_part != "/" else "__default"
    filepath = os.path.join(pastes_dir, filename)
    return filepath

def check_paste_name(name:str):
    return name == "" or name.replace("_", "").isalnum()

class ShPasteBinRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _get_post_vars(self):
        # See https://stackoverflow.com/questions/4233218/python-how-do-i-get-key-value-pairs-from-the-basehttprequesthandler-http-post-h
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            data_read = self.rfile.read(length)
            data_read = data_read.decode("utf-8")
            postvars = parse_qs(data_read, 
                                keep_blank_values=1,
                                encoding="utf-8")
        else:
            postvars = {}
        return {k: "".join([e for e in postvars[k]]) for k in postvars}

    def redirect_to(self, location):
        self.send_response(301)
        self.send_header("location", location)
        self.end_headers()

    def _render_invalid_url(self):
        return "Invalid URL!".encode("utf-8")

    def _render_paste(self, url_path_part, paste_content, message=""):
        """Generates an HTML page for the paste with the filepath"""
        js = """
var helpPage = window.location.protocol + "//" + window.location.host + "/help";
function reloadAction(loc) {
    window.location.href = loc;
}
window.onload=function(){
  var text = document.getElementById('pastearea')
  text.focus()

  window.onhashchange = function() {
    text.focus()
  }
}
document.onkeydown = function (e) {
    e = e || window.event;//Get event

    if (!e.ctrlKey) return;

    var code = e.which || e.keyCode; //Get key code

    switch (code) {
        case 83:
            e.preventDefault();
            e.stopPropagation();
            document.getElementById("pasteform").submit();
            break;
        case 82:
            e.preventDefault();
            e.stopPropagation();
            reloadAction(window.location.href);
            break;
    }
};
        """
        css = """
.container {
    width: 90%;
    height: 85%;
    background-color: black;
    padding: 1em;
}

.pastearea {
    height: 100%;
    width: 100%;
    font-size: 2em;
}
body {
    background-color: #003300;
}
        """
        content = f"""
<html>
<head>
    <meta charset="utf-8"/>
    <style>{css}</style>
    <script>{js}</script>
    <title>{url_path_part} ShPasteBin</title>        
</head>
<body>
    <p>{message}</p>
    <p>
    <form action="{url_path_part}" method="post" id="pasteform" style="display:inline;">
        <input type="submit" value="Save (CTRL-S)" id="saveButton">
    </form> 
    <button onClick="reloadAction(window.location.href);">Reload (CTRL-R)</button>
    <button onClick="reloadAction(helpPage);">Help</button>
</p>
    <div class="container">
    <textarea class="pastearea" name="paste" form="pasteform" id="pastearea">{paste_content}</textarea>
    </div>
</body>
</html>"""
        return content.encode("utf8")

    def do_GET(self):
        self._set_headers()
        if not check_paste_name(self.path[1:]):
            self.wfile.write(self._render_invalid_url())
            return
        filepath = get_paste_path(self.path)
        create_if_not_existing(filepath)
        paste_content = get_file_content(filepath)
        self.wfile.write(self._render_paste(self.path, paste_content))

    def do_HEAD(self):
        self._set_headers()


    def do_POST(self):
        if not check_paste_name(self.path[1:]):
            self._set_headers()
            self.wfile.write(self._render_invalid_url())
            return
        filepath = get_paste_path(self.path)
        postvars = self._get_post_vars()
        content = postvars["paste"]
        write_file_content(filepath, content)
        self.redirect_to(self.path)

description = """ShPasteBin is a simple paste bin server."""
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-a",
                    "--address",
                    help="""The address to listen to (default value = 0.0.0.0)""",
                    action="store",
                    default="0.0.0.0")
parser.add_argument("-p",
                    "--port",
                    help="""The port to listen to (default value = 8701)""",
                    action="store",
                    default="8701")
parser.add_argument("-d",
                    "--pastes_dir",
                    help="""The directory where the pastes are stored (default value is the pastes directory in the same directory as this script)""",
                    action="store",
                    default=pastes_dir)
args = parser.parse_args()

server_address = (args.address, int(args.port))
pastes_dir = args.pastes_dir
server = HTTPServer(server_address, ShPasteBinRequestHandler)
print("Starting server: http://" + server_address[0] + ":" + str(server_address[1]))
server.serve_forever()