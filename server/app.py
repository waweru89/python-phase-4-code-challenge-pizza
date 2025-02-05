#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    body = [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants]
    return make_response(body, 200)
@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def get_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if request.method == "DELETE":
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 200)
    
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    body = restaurant.to_dict()
    return make_response(body, 200)

@app.route("/pizzas" , methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    body = [pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas]
    return make_response(body, 200)

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizzas():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")
    if not all([price, pizza_id, restaurant_id]):
        return make_response({"error": "Missing required fields"}, 400)
    new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(new_restaurant_pizza)
    db.session.commit()
    return make_response(new_restaurant_pizza.to_dict(), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
