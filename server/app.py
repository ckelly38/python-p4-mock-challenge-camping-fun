#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

api = Api(app);

db.init_app(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        cmprs = [cmpr.to_dict(rules=("-signups",)) for cmpr in Camper.query.all()];
        return cmprs, 200;

    def post(self):
        #print("INSIDE ADD NEW CAMPER-POST():");
        rjsn = request.get_json();
        #rdta = request.get_data();
        #rfrm = request.form;
        #print(rjsn);
        #print(rdta);
        #print(rfrm);
        ncmpr = None;
        try:
            ncmpr = Camper(name=rjsn["name"], age=rjsn["age"]);
        except Exception as ex:
            #print("400 ERROR: INVALID CAMPER!");
            return {"errors": ["validation errors"]}, 400;
        #add it to the database now
        db.session.add(ncmpr);
        db.session.commit();
        return ncmpr.to_dict(), 201;

api.add_resource(Campers, "/campers");

class CamperByID(Resource):
    def get(self, id):
        cmpr = Camper.query.filter_by(id=id).first();
        if (cmpr == None): return {"error": "Camper not found"}, 404;
        else: return cmpr.to_dict(), 200;

    def patch(self, id):
        cmpr = Camper.query.filter_by(id=id).first();
        if (cmpr == None): return {"error": "Camper not found"}, 404;
        rjsn = request.get_json();
        #print(rjsn);
        try:
            for attr in rjsn:
                setattr(cmpr, attr, rjsn[attr]);
        except Exception as ex:
            #print("400 ERROR: INVALID CAMPER!");
            return {"errors": ["validation errors"]}, 400;
        return cmpr.to_dict(), 202;
        #print("404 ERROR: NOT DONE WITH UPDATING A CAMPER!");
        #return {"error": "404 ERROR: NOT DONE YET WITH UPDATING A CAMPER!"}, 404;

api.add_resource(CamperByID, "/campers/<int:id>");

class Activities(Resource):
    def get(self):
        acts = [act.to_dict() for act in Activity.query.all()];
        return acts, 200;

api.add_resource(Activities, "/activities");

class ActivityByID(Resource):
    def delete(self, id):
        act = Activity.query.filter_by(id=id).first();
        if (act == None): return {"error": "Activity not found"}, 404;
        #remove it from the database
        db.session.delete(act);
        db.session.commit();
        return {}, 204;
        #print("404 ERROR: NOT DONE WITH DELETING ACTIVITIES!");
        #return {"error": "404 ERROR: NOT DONE YET WITH DELETING ACTIVITIES!"}, 404;

api.add_resource(ActivityByID, "/activities/<int:id>");

class SignUps(Resource):
    def post(self):
        rjsn = request.get_json();
        print(rjsn);
        snup = None;
        try:
            snup = Signup(activity_id=rjsn["activity_id"], camper_id=rjsn["camper_id"],
                          time=rjsn["time"]);
        except Exception as ex:
            #print("400 ERROR: INVALID SIGNUP!");
            return {"errors": ["validation errors"]}, 400;
        #add it to the database
        db.session.add(snup);
        db.session.commit();
        return snup.to_dict(), 200;
        #print("404 ERROR: NOT DONE WITH MAKING SIGNUPS!");
        #return {"error": "404 ERROR: NOT DONE YET WITH MAKING SIGNUPS!"}, 404;

api.add_resource(SignUps, "/signups");

if __name__ == '__main__':
    app.run(port=5555, debug=True)
