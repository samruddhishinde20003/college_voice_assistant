from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

# Create Flask app
app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/voice_assistant"
mongo = PyMongo(app)

# Home route
@app.route('/')
def home():
    return "Welcome to the Flask App connected to MongoDB!"

# ---------------------------------------
# Routes for `events` collection
# ---------------------------------------
@app.route('/events', methods=['GET'])
def get_events():
    events = mongo.db.events.find()
    event_list = []
    for event in events:
        event['_id'] = str(event['_id'])  # Convert ObjectId to string
        event_list.append(event)
    return jsonify(event_list)

@app.route('/add-event', methods=['POST'])
def add_event():
    new_event = request.json
    mongo.db.events.insert_one(new_event)
    return jsonify({"message": "Event added successfully!"})

# ---------------------------------------
# Routes for `faculty` collection
# ---------------------------------------
@app.route('/faculty', methods=['GET'])
def get_faculty():
    faculty_members = mongo.db.faculty.find()
    faculty_list = []
    for faculty in faculty_members:
        faculty['_id'] = str(faculty['_id'])  # Convert ObjectId to string
        faculty_list.append(faculty)
    return jsonify(faculty_list)

@app.route('/add-faculty', methods=['POST'])
def add_faculty():
    new_faculty = request.json
    mongo.db.faculty.insert_one(new_faculty)
    return jsonify({"message": "Faculty member added successfully!"})

# ---------------------------------------
# Routes for `department` collection
# ---------------------------------------
@app.route('/departments', methods=['GET'])
def get_departments():
    departments = mongo.db.department.find()
    department_list = []
    for department in departments:
        department['_id'] = str(department['_id'])  # Convert ObjectId to string
        department_list.append(department)
    return jsonify(department_list)

@app.route('/add-department', methods=['POST'])
def add_department():
    new_department = request.json
    mongo.db.department.insert_one(new_department)
    return jsonify({"message": "Department added successfully!"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
