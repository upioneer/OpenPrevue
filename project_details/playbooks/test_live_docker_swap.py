import http.client
import socket
import json
import time
import subprocess
import sys

class DockerUDS:
    def __init__(self, path="/var/run/docker.sock"):
        self.path = path

    def request(self, method, url, body=None, headers=None):
        headers = headers or {}
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        conn = http.client.HTTPConnection("localhost")
        conn.sock = sock
        if body and isinstance(body, dict):
            body_str = json.dumps(body)
            headers["Content-Type"] = "application/json"
        elif body and isinstance(body, str):
            body_str = body
        else:
            body_str = None
        conn.request(method, url, body=body_str, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        return resp.status, data

d = DockerUDS()

# Clean any leftover containers
subprocess.run(["docker", "rm", "-f", "test-v1", "test-v1-retiring", "test-swapper"], capture_output=True)

# 1. Start test-v1 container on port 18080
print("1. Launching test-v1 on port 18080...")
subprocess.run(["docker", "run", "-d", "--name", "test-v1", "-p", "18080:8080", "python:3.12-slim", "python3", "-m", "http.server", "8080"], check=True)
time.sleep(1.5)

# 2. Inspect test-v1
status, data = d.request("GET", "/containers/test-v1/json")
info = json.loads(data.decode())
old_id = info["Id"]
print(f"test-v1 running, ID: {old_id[:12]}")

# 3. Rename test-v1 to test-v1-retiring
print("2. Renaming test-v1 to test-v1-retiring...")
status, _ = d.request("POST", f"/containers/{old_id}/rename?name=test-v1-retiring")
print(f"Rename status: {status}")

# 4. Create new container test-v1 with preserved port mappings
print("3. Creating new test-v1 container (stopped)...")
create_payload = {
    "Image": "python:3.12-slim",
    "Cmd": ["python3", "-m", "http.server", "8080"],
    "HostConfig": info.get("HostConfig", {}),
}
status, data = d.request("POST", "/containers/create?name=test-v1", body=create_payload)
new_info = json.loads(data.decode())
new_id = new_info["Id"]
print(f"New container created, ID: {new_id[:12]}, status: {status}")

# 5. Create and run the Ephemeral Swapper Container
print("4. Creating ephemeral swapper container...")
swapper_script = f"""
import http.client, socket, time, sys

time.sleep(1.5)
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/var/run/docker.sock')
conn = http.client.HTTPConnection('localhost')
conn.sock = sock

# Stop old container
print('Swapper: stopping old container {old_id[:12]}...')
conn.request('POST', '/containers/{old_id}/stop?t=5')
resp = conn.getresponse()
print('Stop status:', resp.status)
resp.read()

# Start new container
print('Swapper: starting new container {new_id[:12]}...')
sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock2.connect('/var/run/docker.sock')
conn2 = http.client.HTTPConnection('localhost')
conn2.sock = sock2
conn2.request('POST', '/containers/{new_id}/start')
resp2 = conn2.getresponse()
print('Start status:', resp2.status)
resp2.read()

# Delete old container
sock3 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock3.connect('/var/run/docker.sock')
conn3 = http.client.HTTPConnection('localhost')
conn3.sock = sock3
conn3.request('DELETE', '/containers/{old_id}?v=true')
resp3 = conn3.getresponse()
print('Delete status:', resp3.status)
resp3.read()
print('Swapper handoff completed successfully!')
"""

swapper_payload = {
    "Image": "python:3.12-slim",
    "User": "0:0",
    "Cmd": ["python3", "-c", swapper_script],
    "HostConfig": {
        "AutoRemove": True,
        "Binds": ["/var/run/docker.sock:/var/run/docker.sock"]
    }
}
status, data = d.request("POST", "/containers/create?name=test-swapper", body=swapper_payload)
swapper_id = json.loads(data.decode())["Id"]
print(f"Swapper container created: {swapper_id[:12]}")

print("5. Starting swapper container...")
status, _ = d.request("POST", f"/containers/{swapper_id}/start")
print(f"Swapper start status: {status}")

# 6. Monitor transition
print("6. Monitoring container swap on port 18080...")
success = False
for i in range(12):
    time.sleep(1)
    res = subprocess.run(["docker", "inspect", "--format={{.Id}} {{.State.Status}}", "test-v1"], capture_output=True, text=True)
    out = res.stdout.strip()
    print(f"T+{i+1}s test-v1 status: {out}")
    if new_id in out and "running" in out:
        print(f"\nSUCCESS! New container {new_id[:12]} is running on port 18080!")
        success = True
        break

# Verify port connectivity
if success:
    res = subprocess.run(["curl", "-s", "-I", "http://localhost:18080"], capture_output=True, text=True)
    print("\nCurl verification on port 18080:")
    print(res.stdout[:200])

# Cleanup
subprocess.run(["docker", "rm", "-f", "test-v1", "test-v1-retiring"], capture_output=True)
if not success:
    sys.exit(1)
