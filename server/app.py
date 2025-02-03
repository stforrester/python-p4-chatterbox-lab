from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    
    if request.method == 'GET':
        messages = [message.to_dict() for message in Message.query.order_by(Message.created_at.asc()).all()]
        return make_response(messages, 200)
    
    elif request.method == 'POST':
        data = request.get_json()

        if not data or "body" not in data or "username" not in data:
            return make_response({"error": "Missing required fields"}, 400)

        new_message = Message(
            body=data["body"],
            username=data["username"],
        )

        db.session.add(new_message)
        db.session.commit()

        new_message_dict = new_message.to_dict()

        response = make_response(
            new_message_dict,
            201
        )

        return response

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if message == None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)

        return response
    
    else:
        if request.method == 'GET':
            message_serialized = message.to_dict()
            return make_response( message_serialized, 200 )
        
        elif request.method == 'PATCH':
            data = request.get_json()
            
            message.body = data["body"]

            db.session.add(message)
            db.session.commit()

            updated_message = message.to_dict()

            response = make_response(
                updated_message,
                200
            )

            return response
        
        elif request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Message deleted."
            }

            response = make_response(response_body, 200)

            return response

if __name__ == '__main__':
    app.run(port=5555)
