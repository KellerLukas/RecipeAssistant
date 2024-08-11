import os

def set_api_key(env_var:str):
    if os.getenv(env_var) is None:
        key = input(f"Enter Api Key for {env_var}: ")
        os.environ[env_var] = key