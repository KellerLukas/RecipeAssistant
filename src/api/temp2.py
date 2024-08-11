from src.api.recipe_client import RecipeClient
from src.llm.smart_recipe_client import SmartRecipeClient
import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

client = SmartRecipeClient(openai_op_key_uuid="2m25xpqieooxvazcfhbprtphbq", spoonacular_op_key_uuid="tqw5mdfslmyfzjkggb36ujhcbu")

#ToDo: summarize the summary to a few sentences
id = client.search_recipes('fries')[0]

recipe = client.get_recipe_details(id)
recipe = client.summarize_recipe(recipe)
recipe = client.translate_parts(recipe)


recipe = client.get_recipe_details(id)
recipe = client.summarize_recipe(recipe)
recipe = client.translate_parts(recipe)


pass

