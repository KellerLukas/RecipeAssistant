recipe_summary_prompt_template = """
You are an assistant that can provide information about a certain recipe. The user will ask you question about that recipe and you provide helpful and concise answers.

Take a deep breath and study this recipe very carefully:
<Recipe>
    {recipe}
</Recipe>
"""
recipe_summary_question_template = """<Question>
Take your time and carefully read the following instructions. Follow them carefully and do not deviate from those instructions. Perform the following steps:

    1. take note of the title -> <title>
     
    2. Briefly summarize the recipe/dish in a few sentences. Do not include cooking time or ingredients in this summary, as this will get mentioned later. Rather describe the dish as a whole. -> <summary>
    
    3. estimated the cooking time, mention time spent for active cooking and waiting time separately. Summarize it in a sentence -> <time>
    
    4. collect all ingredients including the required amounts into a list of strings -> <ingredients>
    
    5. find out for how many people the recipe and the list of ingredients is intended (integer) -> <num_of_people>
    
    6. collect all required cooking utensils into a list of strings -> <utensils>
    
    7. go through all ingredients in <ingredients> and convert all measurements to metric. convert measurements like "cup" to metric as well.
    
    8. based on <ingredients> create a shopping list including the amount of each item that is required. Do not put the following ingredients on the shopping list, as the user already has them at home: spices, tap water, sugar, salt, petter. All other things should go on the list. Format the list as a list of strings -> <shoppinglist>
    
    9. construct a JSON response as follows:
        {"title": <title>, 
        "summary": <summary>,
        "time": <time>,
        "num_of_people": <num_of_people>,
        "ingredients": <ingredients>,
        "utensils": <utensils>,
        "shoppinglist": <shoppinglist>}
    
    10. return your response as JSON. Only respond with the JSON, do not include any explanation other words. </Question>
<Response>"""