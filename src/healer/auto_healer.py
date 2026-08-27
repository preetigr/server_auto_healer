# auto_healer.py
import docker
import requests
import time
import sys
from datetime import datetime

TARGET_CONTAINER = "target-app"
HEALTH_URL = "http://127.0.0.1:8080/health"
POLL_INTERVAL = 3

client = docker.from_env()

def is_running(name):
    try:
        container = client.containers.get(name)
        # Reload container state to get fresh status
        container.reload()
        return container.status == "running", container
    except docker.errors.NotFound:
        return False, None
    except Exception as e:
        print(f"[ERROR] Docker API error: {e}", flush=True)
        return False, None

def check_health(url):
    try:
        # 1.0s connect timeout, 1.0s read timeout
        res = requests.get(url, timeout=(1.0, 1.0))
         return res.status_code == 200
    except requests.exceptions.RequestException:
        return False

def main():
    print(f"[*] SRE Auto-Healer active for '{TARGET_CONTAINER}'", flush=True)
    print(f"[*] Polling '{HEALTH_URL}' every {POLL_INTERVAL}s...\n", flush=True)

    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        running, container = is_running(TARGET_CONTAINER)
        healthy = check_health(HEALTH_URL)

        if not running or not healthy:
            print(f"\n[{timestamp} ALERT] Failure detected! (Running: {running}, Healthy: {healthy})", flush=True)
            if container:
                try:
                    container.restart(timeout=3)
                    print(f"[{timestamp} ACTION] Issued 'docker restart {TARGET_CONTAINER}'", flush=True)
                except Exception as e:
                    print(f"[{timestamp} ERROR] Restart failed: {e}", flush=True)
            else:
                print(f"[{timestamp} ERROR] Container '{TARGET_CONTAINER}' not found.", flush=True)
                sys.exit(1)

            recovered = False
            for attempt in range(1, 6):
                time.sleep(2)
                 if check_health(HEALTH_URL):
                    print(f"[{timestamp} SUCCESS] Health check passed on attempt {attempt}! Recovered.\n", flush=True)
                    recovered = True
                    break
                print(f"[{timestamp} WAIT] Attempt {attempt}/5: waiting for container to become healthy...", flush=True)

            if not recovered:
                print(f"[{timestamp} CRITICAL] Automated recovery failed. Escalating.\n", flush=True)
        else:
            print(f"[{timestamp} STATUS] Container is healthy (200 OK)", flush=True)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()