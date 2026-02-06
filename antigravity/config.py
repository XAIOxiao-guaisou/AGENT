import json
import os
import sys

CONFIG_PATH = os.path.join(os.getcwd(), 'config', 'settings.json')

def load_config():
    """
    Load configuration from settings.json and environment variables.
    Environment variables override JSON settings.
    """
    config = {}
    
    # 1. Load from JSON
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading settings.json: {e}")
            sys.exit(1)
    
    # 2. Override with Env Vars
    if os.getenv("DEEPSEEK_API_KEY"):
        config["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
        
    for key in ["TEMPERATURE", "MAX_TOKENS", "RETRY_LIMIT"]:
        val = os.getenv(key)
        if val:
             try:
                 if "." in val:
                     config[key] = float(val)
                 else:
                     config[key] = int(val)
             except ValueError:
                 pass
                 
    return config

# Global Config Object
CONFIG = load_config()
