import json
import time
import logging
from openai import OpenAI
from langchain.prompts import (
    PromptTemplate
)

from src.api.api_client_base import APIClientBase
from src.api.recipe_client import RecipeClient
from src.llm.prompts.recipe_search_prompt import (
    recipe_search_prompt_template,
    recipe_search_question_template,
    recipe_search_retry_addon,
)
from src.llm.prompts.recipe_summary_prompt import (recipe_summary_prompt_template,
    recipe_summary_question_template)
from src.llm.prompts.recipe_translation_prompt import (recipe_translation_prompt_template,
    recipe_translation_question_template)
from src.api.cache_method import CacheMethod

MAX_ATTEMPTS = 10
TOOL_TIMEOUT = 20

demo_recipe ='{"vegetarian": false, "vegan": false, "glutenFree": true, "dairyFree": true, "veryHealthy": false, "cheap": false, "veryPopular": false, "sustainable": false, "lowFodmap": false, "weightWatcherSmartPoints": 10, "gaps": "no", "preparationMinutes": null, "cookingMinutes": null, "aggregateLikes": 14, "healthScore": 1, "creditsText": "Foodista.com \\u2013 The Cooking Encyclopedia Everyone Can Edit", "license": "CC BY 3.0", "sourceName": "Foodista", "pricePerServing": 52.87, "extendedIngredients": [{"id": 10020061, "aisle": "Health Foods", "image": "white-powder.jpg", "consistency": "SOLID", "name": "rice flour", "nameClean": "sweet rice flour", "original": "3/4 cup sweet rice flour", "originalName": "sweet rice flour", "amount": 0.75, "unit": "cup", "meta": ["sweet"], "measures": {"us": {"amount": 0.75, "unitShort": "cups", "unitLong": "cups"}, "metric": {"amount": 120.0, "unitShort": "g", "unitLong": "grams"}}}, {"id": 20648, "aisle": "Baking", "image": "brown-flour.jpg", "consistency": "SOLID", "name": "sorghum flour", "nameClean": "sorghum flour", "original": "3/4 cup sorghum flour", "originalName": "sorghum flour", "amount": 0.75, "unit": "cup", "meta": [], "measures": {"us": {"amount": 0.75, "unitShort": "cups", "unitLong": "cups"}, "metric": {"amount": 90.0, "unitShort": "g", "unitLong": "grams"}}}, {"id": 93696, "aisle": "Baking", "image": "white-powder.jpg", "consistency": "SOLID", "name": "arrowroot", "nameClean": "tapioca starch", "original": "1/2 cup arrowroot (or tapioca starch)", "originalName": "arrowroot (or tapioca starch)", "amount": 0.5, "unit": "cup", "meta": ["(or tapioca starch)"], "measures": {"us": {"amount": 0.5, "unitShort": "cups", "unitLong": "cups"}, "metric": {"amount": 60.0, "unitShort": "g", "unitLong": "grams"}}}, {"id": 93760, "aisle": "Gluten Free", "image": "teff-flour.jpg", "consistency": "SOLID", "name": "teff flour", "nameClean": "teff flour", "original": "1/4 cup teff flour", "originalName": "teff flour", "amount": 0.25, "unit": "cup", "meta": [], "measures": {"us": {"amount": 0.25, "unitShort": "cups", "unitLong": "cups"}, "metric": {"amount": 30.0, "unitShort": "g", "unitLong": "grams"}}}, {"id": 18370, "aisle": "Baking", "image": "white-powder.jpg", "consistency": "SOLID", "name": "aluminum free baking powder", "nameClean": "aluminum free baking powder", "original": "2 teaspoons aluminum free baking powder", "originalName": "aluminum free baking powder", "amount": 2.0, "unit": "teaspoons", "meta": [], "measures": {"us": {"amount": 2.0, "unitShort": "tsps", "unitLong": "teaspoons"}, "metric": {"amount": 2.0, "unitShort": "tsps", "unitLong": "teaspoons"}}}, {"id": 18372, "aisle": "Baking", "image": "white-powder.jpg", "consistency": "SOLID", "name": "baking soda", "nameClean": "baking soda", "original": "1 teaspoon baking soda", "originalName": "baking soda", "amount": 1.0, "unit": "teaspoon", "meta": [], "measures": {"us": {"amount": 1.0, "unitShort": "tsp", "unitLong": "teaspoon"}, "metric": {"amount": 1.0, "unitShort": "tsp", "unitLong": "teaspoon"}}}, {"id": 2025, "aisle": "Spices and Seasonings", "image": "ground-nutmeg.jpg", "consistency": "SOLID", "name": "nutmeg", "nameClean": "nutmeg", "original": "1/2 teaspoon nutmeg", "originalName": "nutmeg", "amount": 0.5, "unit": "teaspoon", "meta": [], "measures": {"us": {"amount": 0.5, "unitShort": "tsps", "unitLong": "teaspoons"}, "metric": {"amount": 0.5, "unitShort": "tsps", "unitLong": "teaspoons"}}}, {"id": 2010, "aisle": "Spices and Seasonings", "image": "cinnamon.jpg", "consistency": "SOLID", "name": "cinnamon", "nameClean": "cinnamon", "original": "1/2 teaspoon cinnamon", "originalName": "cinnamon", "amount": 0.5, "unit": "teaspoon", "meta": [], "measures": {"us": {"amount": 0.5, "unitShort": "tsps", "unitLong": "teaspoons"}, "metric": {"amount": 0.5, "unitShort": "tsps", "unitLong": "teaspoons"}}}, {"id": 99005, "aisle": "Baking", "image": "sugar-in-bowl.png", "consistency": "SOLID", "name": "xylitol", "nameClean": "xylitol", "original": "4 tablespoons Xylitol", "originalName": "Xylitol", "amount": 4.0, "unit": "tablespoons", "meta": [], "measures": {"us": {"amount": 4.0, "unitShort": "Tbsps", "unitLong": "Tbsps"}, "metric": {"amount": 4.0, "unitShort": "Tbsps", "unitLong": "Tbsps"}}}, {"id": 98848, "aisle": "Health Foods", "image": "chocolate-chips.jpg", "consistency": "SOLID", "name": "chocolate vegan chocolate chips", "nameClean": "allergy friendly chocolate chips", "original": "1/2 dark chocolate vegan chocolate chips (I like Enjoy chips)", "originalName": "dark chocolate vegan chocolate chips (I like Enjoy chips)", "amount": 0.5, "unit": "", "meta": ["dark", "(I like Enjoy chips)"], "measures": {"us": {"amount": 0.5, "unitShort": "", "unitLong": ""}, "metric": {"amount": 0.5, "unitShort": "", "unitLong": ""}}}, {"id": 12117, "aisle": "Canned and Jarred", "image": "coconut-milk.png", "consistency": "LIQUID", "name": "coconut milk", "nameClean": "unsweetened coconut milk", "original": "1 cup coconut milk (vanilla), unsweetened", "originalName": "coconut milk (vanilla), unsweetened", "amount": 1.0, "unit": "cup", "meta": ["unsweetened", "(vanilla)"], "measures": {"us": {"amount": 1.0, "unitShort": "cup", "unitLong": "cup"}, "metric": {"amount": 240.0, "unitShort": "ml", "unitLong": "milliliters"}}}, {"id": 9152, "aisle": "Produce", "image": "lemon-juice.jpg", "consistency": "LIQUID", "name": "juice of lemon", "nameClean": "lemon juice", "original": "Juice of 1 lemon", "originalName": "Juice of lemon", "amount": 1.0, "unit": "", "meta": [], "measures": {"us": {"amount": 1.0, "unitShort": "", "unitLong": ""}, "metric": {"amount": 1.0, "unitShort": "", "unitLong": ""}}}, {"id": 9019, "aisle": "Canned and Jarred", "image": "applesauce.png", "consistency": "SOLID", "name": "pear sauce", "nameClean": "applesauce", "original": "4 tablespoons pear sauce or applesauce", "originalName": "pear sauce or applesauce", "amount": 4.0, "unit": "tablespoons", "meta": [], "measures": {"us": {"amount": 4.0, "unitShort": "Tbsps", "unitLong": "Tbsps"}, "metric": {"amount": 4.0, "unitShort": "Tbsps", "unitLong": "Tbsps"}}}, {"id": 4584, "aisle": "Oil, Vinegar, Salad Dressing", "image": "vegetable-oil.jpg", "consistency": "LIQUID", "name": "sunflower oil", "nameClean": "sunflower oil", "original": "1/4 cup sunflower oil", "originalName": "sunflower oil", "amount": 0.25, "unit": "cup", "meta": [], "measures": {"us": {"amount": 0.25, "unitShort": "cups", "unitLong": "cups"}, "metric": {"amount": 54.5, "unitShort": "ml", "unitLong": "milliliters"}}}, {"id": 1082047, "aisle": "Spices and Seasonings", "image": "salt.jpg", "consistency": "SOLID", "name": "kosher salt", "nameClean": "kosher salt", "original": "pinch of kosher salt", "originalName": "pinch of kosher salt", "amount": 1.0, "unit": "pinch", "meta": [], "measures": {"us": {"amount": 1.0, "unitShort": "pinch", "unitLong": "pinch"}, "metric": {"amount": 1.0, "unitShort": "pinch", "unitLong": "pinch"}}}, {"id": 4673, "aisle": "Milk, Eggs, Other Dairy", "image": "light-buttery-spread.png", "consistency": "SOLID", "name": "earth balance soy free spread", "nameClean": "soy buttery spread", "original": "Earth Balance Soy Free Spread, for greasing the skillet", "originalName": "Earth Balance Soy Free Spread, for greasing the skillet", "amount": 12.0, "unit": "servings", "meta": ["for greasing the skillet"], "measures": {"us": {"amount": 12.0, "unitShort": "servings", "unitLong": "servings"}, "metric": {"amount": 12.0, "unitShort": "servings", "unitLong": "servings"}}}], "id": 638939, "title": "Chocolate Chip Pancakes-gluten free, nut free, vegan", "readyInMinutes": 45, "servings": 12, "sourceUrl": "https://www.foodista.com/recipe/TVH4PNC8/chocolate-chip-pancakes-gluten-free-nut-free-vegan", "image": "https://img.spoonacular.com/recipes/638939-556x370.jpg", "imageType": "jpg", "summary": "Chocolate Chip Pancakes-gluten free, nut free, vegan takes around <b>45 minutes</b> from beginning to end. This recipe serves 12 and costs 53 cents per serving. Watching your figure? This gluten free and dairy free recipe has <b>268 calories</b>, <b>2g of protein</b>, and <b>19g of fat</b> per serving. It works well as a side dish. If you have aluminum free baking powder, coconut milk, cinnamon, and a few other ingredients on hand, you can make it. A couple people made this recipe, and 14 would say it hit the spot. It is brought to you by Foodista. Overall, this recipe earns a <b>rather bad spoonacular score of 25%</b>. If you like this recipe, take a look at these similar recipes: <a href=\\"https://spoonacular.com/recipes/chocolate-chip-pancakes-gluten-free-nut-free-vegan-1555785\\">Chocolate Chip Pancakes-gluten free, nut free, vegan</a>, <a href=\\"https://spoonacular.com/recipes/chocolate-sandwich-cookies-with-chocolate-cream-filling-gluten-free-grain-free-nut-free-vegan-paleo-friendly-196382\\">Chocolate Sandwich Cookies with Chocolate Cream Filling (Gluten-Free, Grain-Free, Nut-Free, Vegan, Paleo Friendly)</a>, and <a href=\\"https://spoonacular.com/recipes/creamy-vegan-corn-and-red-pepper-blender-soup-gluten-free-soy-free-nut-free-grain-free-salt-free-520519\\">Creamy Vegan Corn and Red Pepper Blender Soup (gluten-free, soy-free, nut-free, grain-free, salt-free)</a>.", "cuisines": [], "dishTypes": ["side dish"], "diets": ["gluten free", "dairy free"], "occasions": [], "instructions": "Pour the coconut milk into a small bowl and the juice of 1 lemon, set aside for a few minutes to form a citric reaction mimicking buttermilk.\\nIn a large bowl sift all the flours, baking soda, baking powder, kosher salt, cinnamon, and nutmeg, then add the chocolate chips.\\nMeasure the oil, then add pear sauce to the oil.\\nAdd the wet ingredients to the dry ingredients in the large bowl, with a rubber spatula, mix until just combined.\\nSet aside for 10 minutes to let all the ingredients blend.\\nWhen ready, heat a large non-stick skillet over medium high heat and grease with Earth Balance spread, just enough to form a nice coat in the skillet.  Keep the spread on the side, you will need to grease more as you go along.\\nWith a baking measuring cup in 1/4 cup size, scoop up batter and drop into the hot pan.  When you see little bubbles forming it is time to flip the pancakes (1-2 minutes), cook another minute until done.  Serve hot or warm.", "analyzedInstructions": [{"name": "", "steps": [{"number": 1, "step": "Pour the coconut milk into a small bowl and the juice of 1 lemon, set aside for a few minutes to form a citric reaction mimicking buttermilk.", "ingredients": [{"id": 12118, "name": "coconut milk", "localizedName": "coconut milk", "image": "coconut-milk.png"}, {"id": 1230, "name": "buttermilk", "localizedName": "buttermilk", "image": "buttermilk.jpg"}, {"id": 1019016, "name": "juice", "localizedName": "juice", "image": "apple-juice.jpg"}, {"id": 9150, "name": "lemon", "localizedName": "lemon", "image": "lemon.png"}], "equipment": [{"id": 404783, "name": "bowl", "localizedName": "bowl", "image": "https://spoonacular.com/cdn/equipment_100x100/bowl.jpg"}]}, {"number": 2, "step": "In a large bowl sift all the flours, baking soda, baking powder, kosher salt, cinnamon, and nutmeg, then add the chocolate chips.", "ingredients": [{"id": 99278, "name": "chocolate chips", "localizedName": "chocolate chips", "image": "https://spoonacular.com/cdn/ingredients_100x100/chocolate-chips.jpg"}, {"id": 18369, "name": "baking powder", "localizedName": "baking powder", "image": "white-powder.jpg"}, {"id": 18372, "name": "baking soda", "localizedName": "baking soda", "image": "white-powder.jpg"}, {"id": 1082047, "name": "kosher salt", "localizedName": "kosher salt", "image": "salt.jpg"}, {"id": 2010, "name": "cinnamon", "localizedName": "cinnamon", "image": "https://spoonacular.com/cdn/ingredients_100x100/cinnamon.jpg"}, {"id": 2025, "name": "nutmeg", "localizedName": "nutmeg", "image": "ground-nutmeg.jpg"}], "equipment": [{"id": 404783, "name": "bowl", "localizedName": "bowl", "image": "https://spoonacular.com/cdn/equipment_100x100/bowl.jpg"}]}, {"number": 3, "step": "Measure the oil, then add pear sauce to the oil.", "ingredients": [{"id": 0, "name": "sauce", "localizedName": "sauce", "image": ""}, {"id": 9252, "name": "pear", "localizedName": "pear", "image": "pears-bosc.jpg"}, {"id": 4582, "name": "cooking oil", "localizedName": "cooking oil", "image": "vegetable-oil.jpg"}], "equipment": []}, {"number": 4, "step": "Add the wet ingredients to the dry ingredients in the large bowl, with a rubber spatula, mix until just combined.", "ingredients": [], "equipment": [{"id": 404642, "name": "spatula", "localizedName": "spatula", "image": "https://spoonacular.com/cdn/equipment_100x100/spatula-or-turner.jpg"}, {"id": 404783, "name": "bowl", "localizedName": "bowl", "image": "https://spoonacular.com/cdn/equipment_100x100/bowl.jpg"}]}, {"number": 5, "step": "Set aside for 10 minutes to let all the ingredients blend.", "ingredients": [], "equipment": [], "length": {"number": 10, "unit": "minutes"}}, {"number": 6, "step": "When ready, heat a large non-stick skillet over medium high heat and grease with Earth Balance spread, just enough to form a nice coat in the skillet.  Keep the spread on the side, you will need to grease more as you go along.", "ingredients": [{"id": 0, "name": "spread", "localizedName": "spread", "image": ""}], "equipment": [{"id": 404645, "name": "frying pan", "localizedName": "frying pan", "image": "https://spoonacular.com/cdn/equipment_100x100/pan.png"}]}, {"number": 7, "step": "With a baking measuring cup in 1/4 cup size, scoop up batter and drop into the hot pan.  When you see little bubbles forming it is time to flip the pancakes (1-2 minutes), cook another minute until done.", "ingredients": [], "equipment": [{"id": 404766, "name": "measuring cup", "localizedName": "measuring cup", "image": "https://spoonacular.com/cdn/equipment_100x100/measuring-cup.jpg"}, {"id": 404645, "name": "frying pan", "localizedName": "frying pan", "image": "https://spoonacular.com/cdn/equipment_100x100/pan.png"}], "length": {"number": 2, "unit": "minutes"}}, {"number": 8, "step": "Serve hot or warm.", "ingredients": [], "equipment": []}]}], "originalId": null, "spoonacularScore": 30.802736282348633, "spoonacularSourceUrl": "https://spoonacular.com/chocolate-chip-pancakes-gluten-free-nut-free-vegan-638939"}'

class MockRecipeClient(RecipeClient):
    def search_recipes(self, recipe_name, num_of_res: int = 100) -> list[str]:
        if recipe_name.lower() == "french fries":
            return [1,2,3,4,5,6,7,8,9,10]
        return []
    def get_recipe_details(self, recipe_id) -> dict:
        time.sleep(2)
        res = json.loads(demo_recipe)
        res['title'] = str(recipe_id)
        return res

        
    
    

class SmartRecipeClient(APIClientBase):
    def __init__(self, openai_op_key_uuid: str = None, openai_env_var_key:str=None, spoonacular_op_key_uuid: str = None, spoonacular_env_var_key:str=None):
        super().__init__(op_key_uuid=openai_op_key_uuid, env_var_key=openai_env_var_key)
        self.recipe_client = MockRecipeClient(op_key_uuid=spoonacular_op_key_uuid, env_var_key=spoonacular_env_var_key)
        self.llm = OpenAI(api_key=self._api_key)
        
    @CacheMethod
    def _get_api_input(self, dish: str, prev_inputs: list[str]=[]):
        addon = ""
        n_iter = len(prev_inputs)
        if n_iter > 0:
            prev_inputs = " \n ".join(prev_inputs)
            addon_template = PromptTemplate.from_template(recipe_search_retry_addon)
            addon = addon_template.invoke(
                {"n_iter": str(n_iter), "prev_inputs": prev_inputs}
            ).text
        response = self.llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": recipe_search_prompt_template},
            {"role": "user", "content": recipe_search_question_template.replace("{dish}",dish).replace("retry_addon",addon)}])
        content = response.choices[0].message.content
        return content

    @CacheMethod
    def search_recipes(self, dish: str, num_of_res: int = None):
        prev_inputs = []
        while len(prev_inputs) <= MAX_ATTEMPTS:
            logging.debug(f"searching for recipes for dish {dish}, attempt number {len(prev_inputs)}")
            api_input = self._get_api_input(dish=dish, prev_inputs=prev_inputs)
            logging.debug(f"chosen api input {api_input}")
            res = self.recipe_client.search_recipes(api_input, num_of_res=num_of_res)
            if len(res) != 0:
                return res 
            prev_inputs.append(api_input)
        return []

    @CacheMethod
    def get_recipe_details(self, recipe_id) -> dict:
        return self.recipe_client.get_recipe_details(recipe_id=recipe_id)
    
    @CacheMethod
    def summarize_recipe(self, recipe_details: dict) -> dict:
        logging.debug(f"creating summary for recipe {recipe_details['title']}")
        response = self.llm.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": recipe_summary_prompt_template.replace("{recipe}",json.dumps(recipe_details))},
            {"role": "user", "content": recipe_summary_question_template}])
        content = response.choices[0].message.content
        summary = json.loads(content.replace("</Response>",""))
        translated = self.translate_parts(summary)
        summary.update(translated)
        recipe_details["ger_title"] = summary.get('title',"")
        recipe_details["shoppinglist"] = summary.get("shoppinglist",[])
        recipe_details['llm_summary'] = self._summary_to_html(summary)
        return recipe_details

    def _summary_to_html(self, summary:dict) -> str:
        content = f"""
        <p> <strong>Rezept ({summary.get("num_of_people","")}):</strong> {summary.get('summary',"")}</p>
        <p> <strong>Chochziit:</strong> {summary.get('time',"")}</p>
        <p> <strong>Zuetate:</strong> {self._to_html_list(summary.get('ingredients',[]))}</p>
        <p> <strong>Utensilie:</strong> {self._to_html_list(summary.get('utensils',[]))}</p>
        """
        return content
        
    def _to_html_list(self, l:list[str])->str:
        content = "</li>\n<li>".join(l)
        return f"<ul><li>{content}</li></ul>"
        
    @CacheMethod
    def translate_parts(self, parts:dict)-> dict:
        logging.debug("translating parts")
        response = self.llm.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": recipe_translation_prompt_template},
            {"role": "user", "content": recipe_translation_question_template.replace("{content}",json.dumps(parts))}])
        content = response.choices[0].message.content
        parts = json.loads(content.replace("</Response>",""))
        return parts