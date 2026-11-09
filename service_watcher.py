import time
import os
import sys
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Sniper Bot is running 24/7")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[Web] Health server listening on port {port}")
    server.serve_forever()

def run_forever():
    # تشغيل سيرفر الويب في خيط مستقل لإرضاء فحص Render السحابي
    web_thread = threading.Thread(target=run_health_server, daemon=True)
    web_thread.start()

    bot_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    python_exe = sys.executable

    print("[خدمة 24/7] تم بدء حارس التشغيل المستمر للبوت...")
    while True:
        try:
            print("[خدمة 24/7] تشغيل بوت قناص عمق السوق...")
            process = subprocess.Popen([python_exe, "-u", bot_script])
            process.wait()
            print("[خدمة 24/7] توقف البوت، جاري إعادة التشغيل التلقائي خلال 5 ثوانٍ...")
        except Exception as e:
            print(f"[خدمة 24/7] تنبيه خطأ: {e}")
        time.sleep(5)

if __name__ == "__main__":
    run_forever()
