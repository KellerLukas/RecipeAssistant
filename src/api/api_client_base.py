import os
import logging



class APIClientBase:
    def __init__(self, host: str = None, op_key_uuid: str = None, env_var_key:str=None):
        self._host = host
        
        if op_key_uuid:
            self._api_key = self._get_api_key_from_op(op_key_uuid=op_key_uuid)
        elif env_var_key:
            self._api_key = self._get_api_key_from_env_variable(env_var_key=env_var_key)
        else:
            self._api_key = None
    
    def _get_api_key_from_env_variable(self, env_var_key:str):
        return os.getenv(env_var_key)
    
    def _get_api_key_from_op(self, op_key_uuid:str) -> str:
        from onepassword import OnePassword
        op = OnePassword()
        item = op.get_item(uuid=op_key_uuid)
        fields = item["fields"]
        for field in fields:
            if field["id"] == "credential":
                return field["value"]
        logging.error(f"API Key with uuid {op_key_uuid} not found")
        raise ValueError