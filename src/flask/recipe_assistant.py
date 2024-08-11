from flask import Flask, render_template, request
import html
import json
from src.llm.smart_recipe_client import SmartRecipeClient

OPENAI_API_ENV_KEY = "OPENAI_API_KEY"
SPOONACULAR_API_ENV_KEY = "SPOONACULAR_API_KEY"

app = Flask(__name__)

@app.route('/')
def index():
    content = render_template("index.html")
    return content


@app.route('/result', methods = ['POST'])
def result():
    dish = request.form["dish"]
    client = SmartRecipeClient(openai_env_var_key=OPENAI_API_ENV_KEY, spoonacular_env_var_key=SPOONACULAR_API_ENV_KEY)
    try:
        recipe_ids = client.search_recipes(dish=dish, num_of_res=3)
    except ConnectionError as e:
        if e.args[0] == 402:
            return "API quota exceeded."
    recipes = [client.get_recipe_details(id) for id in recipe_ids]
    recipes = [client.summarize_recipe(recipe) for recipe in recipes]
    recipes = [_keep_only_required_keys(recipe) for recipe in recipes]
    content = render_template("result.html")
    content = content.replace("{recipes}", json.dumps(recipes))
    return content


def _keep_only_required_keys(recipe: dict) ->dict:
    out = {}
    for key in ["image", "ger_title", "llm_summary", "sourceUrl", "shoppinglist"]:
        out[key] = recipe[key]
    return out

def _escape_for_html(recipe: dict) ->dict:
    return {key: html.escape(value) for key, value in recipe.items()}




