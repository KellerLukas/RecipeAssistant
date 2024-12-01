# RecipeAssistant
**A (pretty useless) tool to assist in finding recipes with minimal user effort** :wink:

A toy project that combines APIs for OpenAI and [Spoonacular](https://spoonacular.com/food-api) to find recipies. The tool is intended to be used as an iPhone web app, running on a Raspberry Pi

### Functionality:
- Landing page asks the user what he wants to cook.
- User inputs a (possibly pretty vague) description of what he wants to cook (e.g. "something sweet with eggs")
- The LLM takes a guess which dish the user could be referring to
- Spoonacular is searched for any matches for the given query
- If there are no results, the LLM continues to guess until some recipies are found (the spoonacular search is not very forgiving with search inputs...)
- The LLM summarizes each recipe to provide title, summary, cooking time, number of servings, ingredients, required utensils as well as a shopping list
- The LLM then also translates everything to swiss german, just for fun
- The results are displayed to the user using lazy loading techniques to prevent unnecessary API calls and long loading times
- Option to add the shopping list to Apple reminders.

### Future Improvements
- Evaluate whether the returned results from Spoonacular actually match the search query (the results are quite strange sometimes)
- Sort the results by relvance (the available sorting options are not that great)
- Add user authentication of some sort to prevent unauthorized usage of API keys.
