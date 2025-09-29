#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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

# Routes
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

#Get all restaurants
# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    # Use 'only' to prevent complex serialization overhead for this list view
    return jsonify([r.to_dict(only=("id", "name", "address")) for r in restaurants]), 200

#Get restaurant by id
# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
    if not restaurant:
        # Returns 404 if not found
        return jsonify({"error": "Restaurant not found"}), 404
    
    # Returns 200 with the deeply nested JSON structure defined by models.py's serialize_rules
    return jsonify(restaurant.to_dict()), 200

# Delete restaurant by id
# DELETE /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    # commit the changes to the database
    db.session.commit()
    return "", 204

# Get all pizzas
# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    # Use 'only' to prevent complex serialization overhead for this list view
    return jsonify([p.to_dict(only=("id", "name", "ingredients")) for p in pizzas]), 200

# Create a new restaurant_pizza
# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        new_rest_pizza = RestaurantPizza(
            price=data.get("price"),
            pizza_id=data.get("pizza_id"),
            restaurant_id=data.get("restaurant_id"),
        )
        db.session.add(new_rest_pizza)
        db.session.commit()
        
        # When returning the created item, we need to ensure the nested pizza data is present
        # We fetch the created object again to ensure all relationships are loaded
        created_rp = RestaurantPizza.query.get(new_rest_pizza.id)
        # Manual Serialization for Required Nested Output (201 status on success)
        # We manually construct the response data dictionary to ensure the required 
        # nested structure is met, using .to_dict(only=...) on related objects to 
        # prevent potential deep recursion.
        response_data = {
            "id": created_rp.id,
            "price": created_rp.price,
            "pizza_id": created_rp.pizza_id,
            "restaurant_id": created_rp.restaurant_id,
            
            # Nested Pizza data (only name and ingredients needed)
            "pizza": created_rp.pizza.to_dict(only=("id", "name", "ingredients")),
            
            # Nested Restaurant data (only name and address needed)
            "restaurant": created_rp.restaurant.to_dict(only=("id", "name", "address"))
        }
        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        # Return 400 for validation errors
        return jsonify({"errors": ["validation errors", str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)