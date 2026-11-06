"""Lanzador estatico local en puerto 80 para abrir el navegador normal sin numero de puerto."""

import ctypes
import http.server
import os
import socket
import socketserver
import threading
import time
import webbrowser

HOST = "127.0.0.1"
CUSTOM_HOSTNAME = "demoCiberseguridadDigital"
URL_PATH = "/wclifral/login/loginUniCorn"
PREFERRED_PORTS = (80, 8090, 8091, 8092)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"


class DemoStaticHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        # Sirve siempre index.html para cualquier ruta local configurada
        if self.path != "/favicon.ico":
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        # Silencia logs de red/IP en consola
        pass


def is_hostname_configured():
    try:
        socket.gethostbyname(CUSTOM_HOSTNAME)
        return True
    except socket.gaierror:
        return False


def ensure_hostname_in_hosts():
    if is_hostname_configured():
        return True
    print(f"Configurando el alias local '{CUSTOM_HOSTNAME}' en Windows")
    ps_cmd = (
        f"$h = '{HOSTS_FILE}'; "
        f"$c = Get-Content $h -Raw -ErrorAction SilentlyContinue; "
        f"if ($c -notmatch '{CUSTOM_HOSTNAME}') {{ "
        f"Add-Content -Path $h -Value \"`r`n127.0.0.1 {CUSTOM_HOSTNAME}\" -Encoding ASCII "
        f"}}"
    )
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", "powershell.exe", f'-NoProfile -WindowStyle Hidden -Command "{ps_cmd}"', None, 0
    )
    if ret <= 32:
        return False
    for _ in range(15):
        time.sleep(0.4)
        if is_hostname_configured():
            return True
    return is_hostname_configured()


def find_available_port():
    for port in PREFERRED_PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((HOST, port)) != 0:
                return port
    return 0


if __name__ == "__main__":
    has_alias = ensure_hostname_in_hosts()
    chosen_port = find_available_port()
    with socketserver.TCPServer((HOST, chosen_port), DemoStaticHandler) as httpd:
        actual_port = httpd.server_address[1]
        host_for_url = CUSTOM_HOSTNAME if has_alias else "localhost"
        port_suffix = "" if actual_port == 80 else f":{actual_port}"
        url = f"http://{host_for_url}{port_suffix}{URL_PATH}"

        print("========================================================")
        print("  ENTORNO LOCAL DE DEMOSTRACION EDUCATIVA ACTIVO")
        print(f"  URL abierta en tu navegador: {url}")
        print("  (Cierra esta ventana o pulsa Ctrl+C al terminar)")
        print("========================================================")
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDemostracion finalizada.")

