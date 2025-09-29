from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship to the association object RestaurantPizza
    restaurant_pizzas = relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serialization rules for Restaurant
    serialize_rules = (
        "-restaurant_pizzas.restaurant", 
        "-pizzas" # Exclude pizzas to prevent deep nesting in restaurant serialization
    )

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship to the association object RestaurantPizza
    restaurant_pizzas = relationship(
        "RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan"
    )
    restaurants = association_proxy("restaurant_pizzas", "restaurant")
    
    # Serialization rules for Pizza
    serialize_rules = ("-restaurant_pizzas", '-restaurants')
    
    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    
    #Foreign Keys
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    
    # Serialization rules for RestaurantPizza
    # 1. Exclude the full Restaurant object back-reference
    # 2. When serializing RestaurantPizza, explicitly include the nested 'pizza' object, but exclude its back-reference to prevent recursion.
    serialize_rules = (
        "-restaurant", 
        "-pizza.restaurant_pizzas",
    )

    # add validation
    @validates("price")
    def validate_price(self, key, price):
        #Ensure Price is an Integer
        if not isinstance(price, int):
            raise ValueError("Price must be an integer")
        #Ensure Price is between 1 and 30
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"