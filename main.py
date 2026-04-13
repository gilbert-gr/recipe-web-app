from flask import Flask, render_template, request
from data import CATEGORIES
from flask_bootstrap import Bootstrap5
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()


COLOR_PALETTE = {
    "dark pink": "#FF90BB",
    "pink": "#FFC1DA",
    "yellow": "#F8F8E1",
    "green": "#8ACCD5",
    "url": "https://colorhunt.co/palette/ff90bbffc1daf8f8e18accd5",
}

FONTS = {
    "headers": "Young Serif",
    "body": "Instrument Sans",
}


SEARCH_BY_CATEGORY_URL = "https://www.themealdb.com/api/json/v1/1/filter.php"
GET_RECIPE_BY_ID = "https://www.themealdb.com/api/json/v1/1/lookup.php"
GET_RANDOM_MEAL_URL = "https://www.themealdb.com/api/json/v1/1/random.php"
SEARCH_BY_MAIN_INGREDIENT = "https://www.themealdb.com/api/json/v1/1/filter.php"
SEARCH_BY_NAME = "https://www.themealdb.com/api/json/v1/1/search.php"

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")


@app.context_processor
def inject_date():
  return {"date": datetime.now().year}


@app.route("/")
def home():
    example_meals = []
    for n in range(3):
        repeat = True
        example = None
        while repeat:
            response = requests.get(url=GET_RANDOM_MEAL_URL)
            response.raise_for_status()
            example = response.json()["meals"]
            if example not in example_meals:
                repeat = False

        example_meals.append(example)

    return render_template("index.html", example_meals=example_meals)



@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/random-meal")
def get_random_meal():
    response = requests.get(url=GET_RANDOM_MEAL_URL)
    response.raise_for_status()

    meal = response.json()["meals"]

    return render_template("recipe.html", meal=meal)



@app.route("/category-search")
def category_search():
    return render_template("search-by.html", categories=CATEGORIES)


@app.route("/search-by/<string:choice>")
def search_by(choice):
    method = request.args.get("method")
    params = {
        method: choice,
    }
    response = requests.get(url=SEARCH_BY_CATEGORY_URL, params=params)
    response.raise_for_status()
    meals = response.json()["meals"]

    return render_template("meals.html", meals=meals)



@app.route("/get-recipe/<int:meal_id>")
def get_recipe(meal_id):
    params = {
        "i": meal_id,
    }
    response = requests.get(url=GET_RECIPE_BY_ID, params=params)
    response.raise_for_status()

    meal = response.json()["meals"]
    return render_template("recipe.html", meal=meal)


if __name__ == "__main__":
    app.run(debug=True)
