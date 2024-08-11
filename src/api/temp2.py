from src.api.recipe_client import RecipeClient
from src.llm.smart_recipe_client import SmartRecipeClient
import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
client = SmartRecipeClient(openai_op_key_uuid="2m25xpqieooxvazcfhbprtphbq")
#ToDo: summarize the summary to a few sentences
pass

