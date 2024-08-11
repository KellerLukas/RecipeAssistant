import json
import requests
import logging
from src.api.api_client_base import APIClientBase
from src.api.cache_method import CacheMethod

HOST = "https://api.spoonacular.com/recipes"
            

class RecipeClient(APIClientBase):
    def __init__(self, op_key_uuid: str = None, env_var_key:str=None):
        super().__init__(host=HOST, op_key_uuid=op_key_uuid, env_var_key=env_var_key)

    @CacheMethod
    def search_recipes(self, recipe_name, num_of_res: int = 100) -> list[str]:
        logging.debug(f"retrieving recipes for string {recipe_name}")
        url = f"{self._host}/complexSearch"
        params = {
            "query": recipe_name,
            "number": num_of_res,
            "apiKey": self._api_key,
            "sort": "popularity",
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("results")
            if results:
                return [result["id"] for result in results]
            else:
                logging.debug(f"No recipes found for {recipe_name}.")
                return []
        else:
            logging.error(f"Failed to fetch recipe: {response.status_code}")
            raise ConnectionError(response.status_code)

    @CacheMethod
    def get_recipe_details(self, recipe_id) -> dict:
        url = f"{self._host}/{recipe_id}/information"
        params = {"apiKey": self._api_key}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch recipe details: {response.status_code}")
            raise ConnectionError(response.status_code)
