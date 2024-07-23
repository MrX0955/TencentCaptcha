import json
from time import sleep
from curl_cffi import requests

CONFIG_PATH = "config.json"
CAPTCHA_API_URL = "https://api.capmonster.cloud"
CAPTCHA_WEBSITE_URL = ""
CAPTCHA_WEBSITE_KEY = ""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
IMPESONATE_BROWSER = "chrome120"


def load_config(config_path):

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        captcha_key = config.get("captcha_key")
        if not captcha_key:
            raise ValueError("No CAPTCHA key found in config.json")
        return captcha_key
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in configuration file")


def create_captcha_task(client_key):
    
    task_data = {
        "clientKey": client_key,
        "task": {
            "type": "CustomTask",
            "class": "TenDI",
            "websiteURL": CAPTCHA_WEBSITE_URL,
            "websiteKey": CAPTCHA_WEBSITE_KEY,
            "userAgent": USER_AGENT,
        },
    }
    response = requests.post(
        f"{CAPTCHA_API_URL}/createTask", impersonate=IMPESONATE_BROWSER, json=task_data
    ).json()
    if response.get("errorId") != 0:
        raise RuntimeError(f"Error creating task: {response}")
    return response["taskId"]


def get_captcha_result(client_key, task_id):
    while True:
        response = requests.post(
            f"{CAPTCHA_API_URL}/getTaskResult",
            impersonate=IMPESONATE_BROWSER,
            json={"clientKey": client_key, "taskId": task_id},
        ).json()
        if response["status"] == "processing":
            sleep(3)
            continue
        if response.get("errorId") != 0:
            raise RuntimeError(f"Error retrieving task result: {response}")
        solution = response.get("solution", {}).get("data", {})
        return solution.get("ticket"), solution.get("randstr")


def main():
    try:
        client_key = load_config(CONFIG_PATH)
        task_id = create_captcha_task(client_key)
        ticket, randstr = get_captcha_result(client_key, task_id)
        print("Ticket:", ticket)
        print("Randstr:", randstr)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
