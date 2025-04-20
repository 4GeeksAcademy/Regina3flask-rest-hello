"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

# ========== Standard & External Imports ==========
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS

# ========== Internal Modules ==========
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planets, Starships, FavoriteCharacters, FavoritePlanets, FavoriteStarships

# ========== App Configuration ==========
app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://") if db_url else "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# ========== Error Handling ==========
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# ========== Sitemap ==========
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ========== GET Routes ==========
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify({'data': users_serialized}), 200

@app.route('/character', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    characters_serialized = [character.serialize() for character in characters]
    return jsonify({'data': characters_serialized}), 200

@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify({'data': planets_serialized}), 200

@app.route('/starship', methods=['GET'])
def get_starships():
    starships = Starships.query.all()
    starships_serialized = [starship.serialize() for starship in starships]
    return jsonify({'data': starships_serialized}), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'data': user.serialize()}), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({'message': 'Character not found'}), 404
    return jsonify({'data': character.serialize()}), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'message': 'Planet not found'}), 404
    return jsonify({'data': planet.serialize()}), 200

@app.route('/starship/<int:starship_id>', methods=['GET'])
def get_starship(starship_id):
    starship = Starships.query.get(starship_id)
    if not starship:
        return jsonify({'message': 'Starship not found'}), 404
    return jsonify({'data': starship.serialize()}), 200

@app.route('/favoritecharacter', methods=['GET'])
def get_favorite_characters():
    favorites = FavoriteCharacters.query.all()
    serialized = [fav.serialize() for fav in favorites]
    return jsonify({'data': serialized}), 200

@app.route('/favoriteplanet', methods=['GET'])
def get_favorite_planets():
    favorites = FavoritePlanets.query.all()
    serialized = [fav.serialize() for fav in favorites]
    return jsonify({'data': serialized}), 200

@app.route('/favoritestarship', methods=['GET'])
def get_favorite_starships():
    favorites = FavoriteStarships.query.all()
    serialized = [fav.serialize() for fav in favorites]
    return jsonify({'data': serialized}), 200

@app.route('/user/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    serialized = [fav.serialize() for fav in user.favorites_characters]
    return jsonify({'msg': 'ok', 'favoritos': serialized}), 200

# ========== POST Routes ==========
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password', 'firstName', 'lastName')):
        return jsonify({'message': 'Missing required fields'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    new_user = User(
        email=data['email'],
        password=data['password'],
        firstName=data['firstName'],
        lastName=data['lastName'],
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully', 'user': new_user.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'message': 'Planet not found'}), 404
    db.session.add(FavoritePlanets(planet_id=planet_id))
    db.session.commit()
    return jsonify({'message': f'Planet {planet_id} added to favorites'}), 201

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({'message': 'Character not found'}), 404
    db.session.add(FavoriteCharacters(character_id=character_id))
    db.session.commit()
    return jsonify({'message': f'Character {character_id} added to favorites'}), 201

@app.route('/favorite/starship/<int:starship_id>', methods=['POST'])
def add_favorite_starship(starship_id):
    starship = Starships.query.get(starship_id)
    if not starship:
        return jsonify({'message': 'Starship not found'}), 404
    db.session.add(FavoriteStarships(starship_id=starship_id))
    db.session.commit()
    return jsonify({'message': f'Starship {starship_id} added to favorites'}), 201

# ========== DELETE Routes ==========
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    fav = FavoritePlanets.query.filter_by(planet_id=planet_id).first()
    if not fav:
        return jsonify({'message': 'Favorite planet not found'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': f'Planet {planet_id} removed from favorites'}), 200

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def remove_favorite_character(character_id):
    fav = FavoriteCharacters.query.filter_by(character_id=character_id).first()
    if not fav:
        return jsonify({'message': 'Favorite character not found'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': f'Character {character_id} removed from favorites'}), 200

@app.route('/favorite/starship/<int:starship_id>', methods=['DELETE'])
def remove_favorite_starship(starship_id):
    fav = FavoriteStarships.query.filter_by(starship_id=starship_id).first()
    if not fav:
        return jsonify({'message': 'Favorite starship not found'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': f'Starship {starship_id} removed from favorites'}), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {user_id} deleted successfully'}), 200

# ========== PUT Routes ==========
@app.route('/character/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({'message': 'Character not found'}), 404

    character.name = request.json.get('name', character.name)
    character.gender = request.json.get('gender', character.gender)
    character.height = request.json.get('height', character.height)
    db.session.commit()
    return jsonify({'message': f'Character {character_id} updated successfully', 'character': character.serialize()}), 200

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'message': 'Planet not found'}), 404

    planet.name = request.json.get('name', planet.name)
    planet.weather = request.json.get('weather', planet.weather)
    db.session.commit()
    return jsonify({'message': f'Planet {planet_id} updated successfully', 'planet': planet.serialize()}), 200

@app.route('/starship/<int:starship_id>', methods=['PUT'])
def update_starship(starship_id):
    starship = Starships.query.get(starship_id)
    if not starship:
        return jsonify({'message': 'Starship not found'}), 404

    starship.name = request.json.get('name', starship.name)
    starship.model = request.json.get('model', starship.model)
    db.session.commit()
    return jsonify({'message': f'Starship {starship_id} updated successfully', 'starship': starship.serialize()}), 200
