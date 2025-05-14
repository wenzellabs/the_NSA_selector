#!/usr/bin/env python3

from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from urllib.parse import unquote
import mimetypes
import os

class FileHandler(SimpleHTTPRequestHandler):
    def list_files_with_sizes(self, path="."):
        try:
            with os.scandir(path) as entries:
                files = [(entry.name, entry.stat().st_size) for entry in entries if entry.is_file()]
            return sorted(files, key=lambda x: x[0].lower())
        except FileNotFoundError:
            return []

    def format_size(self, size):
        """Convert a size in bytes to a human-readable string with kB, MB, or GB."""
        for unit in ['bytes', 'kB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def generate_html(self):
        files = self.list_files_with_sizes("files")
        rows = [f'<tr><td>{self.format_size(size)}</td><td><a href="/files/{name}" target="_blank">{name}</a></td></tr>' for name, size in files]
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Files</title>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>Files</h1>
            <table>
                <thead>
                    <tr>
                        <th>Size</th>
                        <th>Filename</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </body>
        </html>
        """
        return html

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.generate_html()
            self.wfile.write(html.encode('utf-8'))
        elif self.path.startswith('/files/'):
            file_path = unquote(self.path[1:])  # decode %xx to unicode
            if os.path.isfile(file_path):
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_response(200)

                if mime_type and mime_type.startswith('image/'):
                    # serve inline in new tab
                    self.send_header('Content-Type', mime_type)
                    self.send_header('Content-Disposition', f'inline; filename="{os.path.basename(file_path)}"')
                else:
                    # force download for all other types
                    self.send_header('Content-Type', mime_type or 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')

                self.end_headers()
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File not found")
        else:
            super().do_GET()

# Specify the port you want to use
port = 8000

# Create a server with the custom handler
handler = FileHandler
ThreadingTCPServer.allow_reuse_address = True
httpd = ThreadingTCPServer(("", port), handler)
httpd.allow_reuse_address = True

print(f"Server started on port {port}")

# Start the server
httpd.serve_forever()

