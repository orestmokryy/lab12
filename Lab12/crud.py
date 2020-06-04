import copy
import json

from flask import Flask, request, jsonify, abort
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from main.model.thermos import Thermos

with open('secret.json') as f:
    SECRET = json.load(f)

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
marshmallow = Marshmallow(app)


class Thermos(Thermos, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capacity_in_liters = db.Column(db.Float, unique=False)
    price_in_uah = db.Column(db.Float, unique=False)
    weight_in_kilograms = db.Column(db.Integer, unique=False)
    producing_country = db.Column(db.String(64), unique=False)
    color = db.Column(db.String(64), unique=False)
    producer = db.Column(db.String(64), unique=False)
    body_material = db.Column(db.String(64), unique=False)

    def __init__(self, capacity_in_liters=0, price_in_uah=0, weigth_in_kilograms=0,
                 production_country="Default", color="Default", producer="Default", body_material="Default"):
        self.capacity_in_liters = capacity_in_liters
        self.price_in_uah = price_in_uah
        self.weigth_in_kilograms = weigth_in_kilograms
        self.production_country = production_country
        self.color = color
        self.producer = producer
        self.body_material = body_material


class ThermosSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'capacity_in_liters', 'price_in_uah', 'weigth_in_kilograms',
                  'production_country', 'color', 'producer', 'body_material')


thermos_schema = ThermosSchema()
thermoses_schema = ThermosSchema(many=True)


@app.route("/add_thermos", methods=["POST"])
def add_thermos():
    capacity_in_liters = request.json['capacity_in_liters']
    price_in_uah = request.json['price_in_uah']
    weigth_in_kilograms = request.json['weigth_in_kilograms']
    production_country = request.json['production_country']
    color = request.json['color']
    producer = request.json['producer']
    body_material = request.json['body_material']
    thermos = Thermos(capacity_in_liters, price_in_uah, weigth_in_kilograms,
                      production_country, color, producer, body_material)
    db.session.add(thermos)
    db.session.commit()
    return thermos_schema.jsonify(thermos)


@app.route("/get_thermos/<id>", methods=["GET"])
def get_wanted_thermos(id):
    thermos = Thermos.query.get(id)
    if not thermos:
        abort(404)
    return thermos_schema.jsonify(thermos)


@app.route("/get_all_thermoses", methods=["GET"])
def get_thermoses():
    all_thermoses = Thermos.query.all()
    result = thermoses_schema.dump(all_thermoses)
    return jsonify({'thermoses': result})


@app.route("/update_thermos/<id>", methods=["PUT"])
def update_thermoses(id):
    thermos = Thermos.query.get(id)
    if not thermos:
        abort(404)
    old_thermos = copy.deepcopy(thermos)
    thermos.capacity_in_liters = request.json['capacity_in_liters']
    thermos.price_in_uah = request.json['price_in_uah']
    thermos.weigth_in_kilograms = request.json['weigth_in_kilograms']
    thermos.production_country = request.json['production_country']
    thermos.color = request.json['color']
    thermos.producer = request.json['producer']
    thermos.body_material = request.json['body_material']
    db.session.commit()
    return thermos_schema.jsonify(old_thermos)


@app.route("/delete_thermos/<id>", methods=["DELETE"])
def delete_thermos(id):
    thermos = Thermos.query.get(id)
    if not thermos:
        abort(404)
    db.session.delete(thermos)
    db.session.commit()
    return f"Deleted thermos with ID:{thermos.id}"


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
