import time
import os
import sys
import subprocess

def run_forever():
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
