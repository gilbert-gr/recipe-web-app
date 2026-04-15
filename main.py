from flask import Flask, render_template, request, flash, redirect, url_for
from data import CATEGORIES, AREAS, INGREDIENTS, RECIPES
from forms import Register, Login
from flask_bootstrap import Bootstrap5
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
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


SEARCH_BY_AREA_OR_CATEGORY_URL = f"https://www.themealdb.com/api/json/v2/{API_KEY}/filter.php"
GET_RECIPE_BY_ID = f"https://www.themealdb.com/api/json/v2/{API_KEY}/lookup.php"
GET_RANDOM_MEAL_URL = f"https://www.themealdb.com/api/json/v2/{API_KEY}/random.php"
GET_10_RANDOM_MEALS = f"https://www.themealdb.com/api/json/v2/{API_KEY}/randomselection.php"
SEARCH_BY_MAIN_INGREDIENT = f"https://www.themealdb.com/api/json/v2/{API_KEY}/filter.php"
SEARCH_BY_NAME = f"https://www.themealdb.com/api/json/v2/{API_KEY}/search.php"

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipes.db"

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

with app.app_context():
    db.create_all()



def fetch_meals(url, params=None):
    response = requests.get(url=url, params=params, timeout=5)
    response.raise_for_status()
    return response.json()["meals"]



@app.context_processor
def inject_date():
  return {"date": datetime.now().year}



@app.route("/")
def home():
    example_meals = fetch_meals(url=GET_10_RANDOM_MEALS)
    print(example_meals)

    return render_template("index.html", example_meals=example_meals)



@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        email = form.email.data

        result = db.session.execute(db.select(User).where(User.email==email))
        user = result.scalar()
        if user:
            flash("You already signed up with this email")
            return redirect(url_for("login"))

        hashed_and_salted_password = generate_password_hash(
            password=form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            username = form.username.data,
            email = email,
            password = hashed_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        password = form.password.data
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email==email))
        user = result.scalar()


        if not user:
            flash("This email does not exist")
            return redirect(url_for("login"))

        if not check_password_hash(pwhash=user.password, password=password):
            flash("Incorrect password")
            return redirect(url_for("login"))

        else:
            login_user(user)
            return redirect(url_for("home"))

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/random-meal")
def get_random_meal():
    meal = fetch_meals(url=GET_RANDOM_MEAL_URL)

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
    meals = fetch_meals(url=SEARCH_BY_AREA_OR_CATEGORY_URL, params=params)

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
        meals = fetch_meals(url=SEARCH_BY_MAIN_INGREDIENT, params=params)

        if not meals:
            flash("There are not recipes with that ingredient, be sure to click an element from the list")
            return redirect(url_for("main_ingredient_search"))

        return render_template("meals.html", meals=meals)
    return render_template("dropdown-search.html", ingredients=INGREDIENTS)



@app.route("/name-search", methods=['GET', 'POST'])
def name_search():
    if request.method == 'POST':
        user_input = request.form["input"]


        if user_input == "Select":
            flash("Please, select a meal")
            return redirect(url_for("name_search"))

        try:
            meal_id = RECIPES[user_input]
        except KeyError:
            flash("Click an element from the list")
            return redirect(url_for("name_search"))

        params = {
            "i": meal_id,
        }
        meal = fetch_meals(url=GET_RECIPE_BY_ID, params=params)
        return render_template("recipe.html", meal=meal)

    return render_template("dropdown-search.html", recipes=RECIPES)



@app.route("/get-recipe/<int:meal_id>")
def get_recipe(meal_id):
    params = {
        "i": meal_id,
    }
    meal = fetch_meals(url=GET_RECIPE_BY_ID, params=params)
    return render_template("recipe.html", meal=meal)


if __name__ == "__main__":
    app.run(debug=True)
