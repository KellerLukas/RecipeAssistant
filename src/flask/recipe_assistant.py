from flask import Flask, render_template, request, jsonify
import html
import json
import logging
from src.llm.smart_recipe_client import SmartRecipeClient

OPENAI_API_ENV_KEY = "OPENAI_API_KEY"
SPOONACULAR_API_ENV_KEY = "SPOONACULAR_API_KEY"

app = Flask(__name__)
client = SmartRecipeClient(openai_env_var_key=OPENAI_API_ENV_KEY, spoonacular_env_var_key=SPOONACULAR_API_ENV_KEY)

@app.route('/')
def index():
    content = render_template("index.html")
    return content


@app.route('/search', methods = ['POST'])
def search():
    dish = request.form["dish"]
    try:
        recipe_ids = client.search_recipes(dish=dish)
    except ConnectionError as e:
        if e.args[0] == 402:
            return "API quota exceeded."
    return jsonify(recipe_ids)

@app.route('/results', methods = ['POST'])
def results():
    recipe_ids = json.loads(request.form["ids"])
    content = render_template("result.html")
    content = content.replace("{recipe_ids}", json.dumps(recipe_ids))
    first_recipe = get_slide_content_for_id(recipe_ids[0])
    content = content.replace("{recipe}", first_recipe)
    return content
    
@app.route('/recipe', methods = ['POST'])
def recipe():
    logging.debug(request.form)
    id = json.loads(request.form['id'])
    return get_slide_content_for_id(id)

def _keep_only_required_keys(recipe: dict) ->dict:
    out = {}
    for key in ["image", "ger_title", "llm_summary", "sourceUrl", "shoppinglist"]:
        out[key] = recipe[key]
    return out

def _escape_for_html(recipe: dict) ->dict:
    return {key: html.escape(value) for key, value in recipe.items()}

def get_slide_content_for_id(id:int)->str:
    recipe = client.get_recipe_details(id)
    recipe = client.summarize_recipe(recipe)
    recipe = _keep_only_required_keys(recipe)
    
    content = f"""
    <img data-src="{recipe['image']}" alt="{recipe['ger_title']}" class="lazy-load">
    <h2><a href="{recipe['sourceUrl']}" target="_blank" style="text-decoration:none">{recipe['ger_title']}</a></h2>
    <button class="shopping-list-button" onclick="addToShoppingList('{recipe['shoppinglist']}')">zur IIchaufsliste</button>
    {recipe['llm_summary']}
    """
    return content


