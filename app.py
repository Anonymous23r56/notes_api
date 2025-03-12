from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import  Migrate 
from app import db, app
from app import User

app = Flask(__name__)

#Secret key for encoding tokens(change this in production)
app.config['JWT_SECRET_KEY'] = jwt = JWTManager(app)
# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Notes model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp=db.Column(db.DateTime, default=datetime.utcnow)
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)


# Create the database tables
with app.app_context():
    db.create_all()
    
with app.app_context():
    new_user = User(username="test_user", email="test@example.com")
    db.session.add(new_user)
    db.session.commit()
    print("User added!")

@app.route('/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    #to check if 'title' and 'content' are in the request 
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content are required"}), 400
    
    new_note = Note(title=data['title'], content=data['content'])
    db.session.add(new_note)
    db.session.commit()    
    
    return jsonify({"message": "Note added successfully","id": new_note.id}), 201

@app.route('/notes',methods=['GET'])
def get_notes():
    notes = Note.query.all()
    notes_list= [{"id": note.id, "title": note.title, "content":note.content}for note in notes]
    return jsonify(notes_list),200

@app.route('/delete_note/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({"message": "Note deleted successfully"}), 200
   
@app.route('/get_notes', methods=['GET'])
def fetch_notes():
    notes = Note.query.all()
    notes_list = [{"id":note.id, "title": note.title, "content": note.content}for note in notes]
    
    return jsonify({"notes": notes_list}), 200

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Notes API!"

if __name__ == '__main__':
    app.run(debug=True)