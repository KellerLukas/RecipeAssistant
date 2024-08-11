import json
import requests
import logging
from src.api.api_client_base import APIClientBase

HOST = "https://api.spoonacular.com/recipes"

class CachedRecipeClient:
    def __init__(self, op_key_uuid: str = None, env_var_key:str=None):
        self.__rc = RecipeClient(op_key_uuid=op_key_uuid, env_var_key=env_var_key)
        self._cache = {}
        
    def search_recipes(self, recipe_name, num_of_res: int = 100) -> list[str]:
        return self._cache_method(self.__rc.search_recipes, recipe_name=recipe_name, num_of_res=num_of_res)
    
    def get_recipe_details(self, recipe_id) -> dict:
        return self._cache_method(self.__rc.get_recipe_details, recipe_id=recipe_id)
        
    def _cache_method(self, method, *args, **kwargs):
        cache = self._cache.get(method.__name__, {})
        key = json.dumps((args,kwargs))
        if key not in cache.keys():
            cache[key] = method(*args, **kwargs)
            self._cache[method.__name__] = cache
        return cache[key]
            

class RecipeClient(APIClientBase):
    def __init__(self, op_key_uuid: str = None, env_var_key:str=None):
        super().__init__(host=HOST, op_key_uuid=op_key_uuid, env_var_key=env_var_key)

    def search_recipes(self, recipe_name, num_of_res: int = 100) -> list[str]:
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

    def get_recipe_details(self, recipe_id) -> dict:
        url = f"{self._host}/{recipe_id}/information"
        params = {"apiKey": self._api_key}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch recipe details: {response.status_code}")
            raise ConnectionError(response.status_code)
