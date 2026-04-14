from flask import Flask, render_template, request, flash, redirect, url_for
from data import CATEGORIES, AREAS, INGREDIENTS
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
}

FONTS = {
    "headers": "Young Serif",
    "body": "Instrument Sans",
}

API_KEY = os.environ.get("API_KEY")


SEARCH_BY_CATEGORY_URL = f"https://www.themealdb.com/api/json/v2/{API_KEY}/filter.php"
GET_RECIPE_BY_ID = f"https://www.themealdb.com/api/json/v2/{API_KEY}/lookup.php"
GET_RANDOM_MEAL_URL = f"https://www.themealdb.com/api/json/v2/{API_KEY}/random.php"
GET_10_RANDOM_MEALS = f"https://www.themealdb.com/api/json/v2/{API_KEY}/randomselection.php"
SEARCH_BY_MAIN_INGREDIENT = f"https://www.themealdb.com/api/json/v2/{API_KEY}/filter.php"
SEARCH_BY_NAME = f"https://www.themealdb.com/api/json/v2/{API_KEY}/search.php"

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")


@app.context_processor
def inject_date():
  return {"date": datetime.now().year}



@app.route("/")
def home():
    response = requests.get(url=GET_10_RANDOM_MEALS)
    response.raise_for_status()
    example_meals = response.json()["meals"]
    print(example_meals)

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


@app.route("/area-search")
def area_search():
    return render_template("search-by.html", areas=AREAS)


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



@app.route("/main-ingredient-search", methods=['GET', 'POST'])
def main_ingredient_search():
    if request.method == 'POST':
        user_input = request.form["input"]

        if user_input == "Select":
            flash("Please, select an ingredient")
            return redirect(url_for("main_ingredient_search"))

        params = {
            "i": user_input
        }
        response = requests.get(url=SEARCH_BY_MAIN_INGREDIENT, params=params)
        response.raise_for_status()
        meals = response.json()["meals"]

        if not meals:
            flash("There are not recipes with that ingredient, be sure to click an element from the list")
            return redirect(url_for("main_ingredient_search"))

        return render_template("meals.html", meals=meals)
    return render_template("dropdown-search.html", ingredients=INGREDIENTS)



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
