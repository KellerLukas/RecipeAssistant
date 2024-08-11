import os
from src.flask.recipe_assistant import app, OPENAI_API_ENV_KEY, SPOONACULAR_API_ENV_KEY
from src.api.set_api_keys import set_api_key



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')