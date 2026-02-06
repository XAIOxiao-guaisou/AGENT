import json
import os
import sys
import yaml

CONFIG_PATH = os.path.join(os.getcwd(), 'config', 'settings.json')
PROMPTS_PATH = os.path.join(os.getcwd(), 'config', 'prompts.yaml')


def load_prompts():
    """
    Load prompts from prompts.yaml.
    Returns dict with prompt configurations.
    """
    if not os.path.exists(PROMPTS_PATH):
        print(f"⚠️ Warning: {PROMPTS_PATH} not found. Using default prompts.")
        return {
            "modes": {
                "executor": {
                    "system_prompt": "You are a code executor. Implement code based on requirements.",
                    "temperature": 0.0,
                    "max_tokens": 4096
                }
            },
            "default_mode": "executor"
        }
    
    try:
        with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
        
        # Validate required keys
        if "modes" not in prompts:
            raise ValueError("prompts.yaml must contain 'modes' key")
        
        return prompts
    except Exception as e:
        print(f"❌ Error loading prompts.yaml: {e}")
        sys.exit(1)

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
    
    # 3. Load prompts
    config["prompts"] = load_prompts()
    
    # 4. Set active mode (can be overridden by env var)
    config["ACTIVE_MODE"] = os.getenv("ACTIVE_MODE", config["prompts"].get("default_mode", "executor"))
                 
    return config

# Global Config Object
CONFIG = load_config()
