import os
import time
import psutil
import sys
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, f"umbaTerminator_{time.strftime('%Y%m%d%H%M%S')}.log")
TARGET_DIR = os.path.join(os.environ["APPDATA"], "Umba")
INTERVAL = 10       
TARGET_PROCESS = ["UmbaWallpaper.exe", "UmbaShare.exe"]

# print(BASE_DIR, LOG_FILE, TARGET_DIR, INTERVAL, TARGET_PROCESS)

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

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
    killUmba()

    log(f"감시 시작: {TARGET_DIR}")
    try:
        while True:
            deleteUmba()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        log("감시 종료")

if __name__ == "__main__":
    main()
