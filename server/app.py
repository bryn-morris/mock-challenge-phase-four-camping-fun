from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
import ipdb

from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# with app.app_context():
#     c1 = Camper()
#     db.session.add(c1)
#     db.session.commit()


@app.route('/')
def index():
    response = make_response(
        {
            "message": "Hello Campers!"
        },
        200
    )
    return response

class Campers(Resource):

    def get(self):

        all_campers = []
        for c in Camper.query.all():
            all_campers.append({
                'id': c.id,
                'name': c.name,
                'age': c.age
            })

        return make_response(all_campers,200)

    def post(self):
        try:
            newCamper = Camper(
                name = request.get_json()['name'],
                age = request.get_json()['age']
            )
            db.session.add(newCamper)
            db.session.commit()
        except:
            response_body = {'errors': ['validation errors']}
            return make_response(response_body, 409)
        else:
            return make_response(newCamper.to_dict(),201)
                
@app.route('/campers/<int:id>', methods = ['GET'])
def campers_by_id(id):
    try:
        if request.method == 'GET':

            selected_camper = Camper.query.filter(Camper.id == id).one()

            id_list = [q.activity_id for q in Signup.query.filter(Signup.camper_id == id).all()]

            associated_act_list = []
            for id in id_list:
                act = Activity.query.filter(Activity.id == id).one()
                associated_act_list.append({
                    'id': act.id,
                    'name': act.name,
                    "difficulty": act.difficulty
                })

            response_body = {
                'id': selected_camper.id,
                'name': selected_camper.name,
                'age': selected_camper.age,
                'activities': associated_act_list
            }
    except:
        response_body = {
                "error": "Camper not found"
            }
        return make_response(response_body, 404)
    else:
        return make_response(response_body, 200)


class Activities(Resource):
    def get(self):

        all_activities = []
        for a in Activity.query.all():
            all_activities.append({
                "id": a.id,
                "name": a.name,
                "difficulty": a.difficulty
            })

        return make_response(all_activities, 200)
    
@app.route('/activities/<int:id>', methods = ['GET', 'DELETE'])
def Activity_by_id(id):
    try: 
        selected_act = Activity.query.filter(Activity.id == id).one()
    except:
        response_body = {
                "error": "Activity not found"
            }
        return make_response(response_body, 404)
    else:
        if request.method == 'GET': 
            return make_response(selected_act.to_dict(), 200)
        elif request.method == 'DELETE':

            counter = 0
            while len(selected_act.signups) >0:
                db.session.delete(selected_act.signups[0])
                db.session.commit()
                counter += 1

            # copy_signups = selected_act.signups.copy()
            
            # for s in copy_signups:
            #     for sel in selected_act.signups:
            #         if sel == s:
            #             db.session.delete(sel)
            #     db.session.commit()

            db.session.delete(selected_act)
            db.session.commit()
            return make_response({},200)
        
class Signups(Resource):

    def get(self):
            all_signups = [s.to_dict() for s in Signup.query.all()]
            return make_response(all_signups, 200)
    def post(self):
        try:
            newSignup = Signup(
                time = request.get_json()['time'],
                camper_id = request.get_json()['camper_id'],
                activity_id = request.get_json()['activity_id']
            )

            db.session.add(newSignup)
            db.session.commit()

        except:
            response_body = {
                "errors": {"validation errors"}
            }
            return make_response(response_body, 422)
        else:

            selected_act = Activity.query.filter(newSignup.activity_id == Activity.id).one()

            response_body = {
                "id": selected_act.id,
                "name": selected_act.name,
                "difficulty": selected_act.difficulty
            }

            return make_response(response_body, 201)

api.add_resource(Signups, '/signups')    
api.add_resource(Activities, '/activities')    
api.add_resource(Campers, '/campers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
