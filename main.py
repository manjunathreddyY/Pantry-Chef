import json
from urllib import response
import requests #To make HTTP requests
from dotenv import load_dotenv #To Scan for .env file and load those key-value pairs
import os #To read the environment values
import google.generativeai as genai #Allows python to load google generative ai models


################################################ API Config ########################################

#calling funciton to load the env variables
load_dotenv()

#Configuring Gemini API
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # This will attempt to read the key from the environment
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini API configured successfully from environment variable.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure GEMINI_API_KEY environment variable is set correctly.")
    print("If using a .env file, ensure it's in the project root.")
    exit() # Exit if configuration fails, as we can't proceed

''' To confirm whether it is connected correctly or not
try:
    response = gemini_model.generate_content("What are you")
    print("\nGemini Response:")
    print(response.text)
except Exception as e:
    print(f"Error during API call: {e}")
'''

# Get Spoonacular API key
try:
    SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
    print("Spoonacular API configured successfully from environment variable.")
except Exception as s: 
    print(f"Error configuring Spoonacular API: {e}")
    print("Please ensure SPOONACULAR_API_KEY environment variable is set correctly.")
    print("If using a .env file, ensure it's in the project root.")
    exit() # Exit if configuration fails, as we can't proceed
    
    
 #################################### Send the ingredients list to LLM ######################################
 
def extract_ingredients_with_gemini(text):
    """Uses Gemini to extract ingredients from user text."""
    prompt = f"""
    You are an expert kitchen assistant. Analyze the following text and extract the food ingredients from it.
    Return the ingredients as a clean, comma-separated string.
    For example, if the input is "I've got some chicken breasts, half an onion, and a can of chopped tomatoes",
    the output should be "chicken breasts, onion, chopped tomatoes".

    Text to analyze: "{text}"
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        print("Gemini's Story:")
        print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your API key is correct and you have network connectivity.")
        
    return response.text.strip()    


#################################### Send the Cleaned ingredients list to Spoonacular ######################################

def find_recipes(ingredients):
    """Finds recipes on Spoonacular based on a comma-separated string of ingredients."""
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    
    params = {
        'ingredients': ingredients,
        'number': 3,  # Let's ask for 3 recipes
        'ranking': 1, # Rank by maximizing used ingredients
        'ignorePantry': True,
        'apiKey': SPOONACULAR_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        return None
 

def summarize_recipes_with_gemini(recipe_data, original_ingredients):
    """Uses Gemini to create a user-friendly summary of the recipes."""
    
    #convert the Python list of recipe data into a string for the prompt
    recipes_str = json.dumps(recipe_data, indent=2)

    prompt = f"""
    You are a cheerful and helpful Pantry Chef.
    Your user has the following ingredients: {original_ingredients}.
    You have found the following recipes for them using an API. The data is in JSON format.

    JSON Data:
    {recipes_str}

    Your task is to present these recipes in a friendly, engaging, and easy-to-read summary.
    For each recipe:
    1. State the recipe's title clearly.
    2. List the ingredients the user already has for that recipe.
    3. List the ingredients they are missing.
    4. Write a short, encouraging sentence about why they should try it.

    Start with a friendly greeting like "Here's what you can make!".
    """
    
    response = gemini_model.generate_content(prompt)
    return response.text.strip()





if __name__ == "__main__":
    print("Welcome to the Pantry Chef! ")
    user_input = input("Please tell me what ingredients you have at home: \n> ")

    #Extracting ingredients using Gemini
    print("\n Analyzing your ingredients...")
    clean_ingredients = extract_ingredients_with_gemini(user_input)
    print(f" Found ingredients: {clean_ingredients}")

    #Finding recipes using Spoonacular
    print("\n🥣 Searching for recipes...")
    recipes = find_recipes(clean_ingredients)
    
    if recipes:
        #Summarizing the results using Gemini
        print("\n Creating a delicious summary for you...")
        summary = summarize_recipes_with_gemini(recipes, clean_ingredients)
        print("\n" + "="*50)
        print(summary)
        print("="*50)
    else:
        print("\nSorry, I couldn't find any recipes. Please try again with different ingredients.")
