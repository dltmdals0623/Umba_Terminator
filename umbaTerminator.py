import os
import time
import psutil
import sys
import threading
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass
import pystray
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "log")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"umbaTerminator_{time.strftime('%Y%m%d%H%M%S')}.log")
LOG_RETENTION_DAYS = 7
TARGET_DIR = os.path.join(os.environ["APPDATA"], "Umba")
INTERVAL = 10       
TARGET_PROCESS = ["UmbaWallpaper.exe", "UmbaShare.exe","UmbaBrownie2.exe"]


stop_event = threading.Event()

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)  

def createTrayImage():
    try:
        return Image.open(os.path.join(BASE_DIR, "images/icon.ico"))
    except OSError:
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((4, 4, 60, 60), fill=(220, 50, 50, 255))
        return img

def watchLoop():
    log(f"감시 시작: {TARGET_DIR}")
    lastClean = time.time()
    try:
        while not stop_event.is_set():
            deleteUmba()
            if time.time() - lastClean >= 24 * 60 * 60:
                cleanOldLogs()
                lastClean = time.time()
            stop_event.wait(INTERVAL)
    finally:
        log("감시 종료")

def onOpenLog(icon, item):
    try:
        os.startfile(BASE_DIR)
    except OSError as e:
        log(f"폴더 열기 실패: {e}")

def onKillNow(icon, item):
    killUmba()
    deleteUmba()

def onQuit(icon, item):
    stop_event.set()
    icon.stop()

def runTray():
    menu = pystray.Menu(
        pystray.MenuItem("로그 폴더 열기", onOpenLog),
        pystray.MenuItem("지금 종료/삭제 실행", onKillNow),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("종료", onQuit),
    )
    icon = pystray.Icon("umbaTerminator", createTrayImage(), "Umba Terminator", menu)
    icon.run()

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

def cleanOldLogs():
    limit = time.time() - LOG_RETENTION_DAYS * 24 * 60 * 60
    try:
        names = os.listdir(LOG_DIR)
    except OSError:
        return
    for name in names:
        if not (name.startswith("umbaTerminator_") and name.endswith(".log")):
            continue
        path = os.path.join(LOG_DIR, name)
        if path == LOG_FILE:
            continue
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < limit:
                os.remove(path)
                log(f"오래된 로그 삭제: {name}")
        except OSError as e:
            log(f"로그 삭제 실패: {name}: {e}")

def killUmba():
    requested = 0
    targets = {name.casefold() for name in TARGET_PROCESS}
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"] or ""
            if name.casefold() not in targets:
                continue

            proc.terminate()
            requested += 1
            log(f"종료 요청: {name} (PID={proc.pid})")

        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            log(f"종료 권한 없음: PID={proc.pid}")

    log(f"총 {requested}개의 대상 프로세스에 종료를 요청했습니다.")

def deleteUmba():
    if not os.path.isdir(TARGET_DIR):
        return
    for name in os.listdir(TARGET_DIR):
        if "umba" not in name.lower() or not name.endswith(".exe"):
            continue
        path = os.path.join(TARGET_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            os.remove(path)
            log(f"삭제 완료: {path}")
        except PermissionError:
            log(f"삭제 실패(실행 중이거나 권한 없음): {path}")
            killUmba()
        except OSError as e:
            log(f"삭제 오류: {path}: {e}")

def main():
    log("프로그램 실행")
    cleanOldLogs()
    killUmba()

    t = threading.Thread(target=watchLoop, daemon=True)
    t.start()

    try:
        runTray()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        t.join(timeout=3)


if __name__ == "__main__":
    main()
