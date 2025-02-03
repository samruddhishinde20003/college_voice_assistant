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
@app.route('/add-event', methods=['POST'])
def add_event():
    new_event = request.json
    mongo.db.events.insert_one(new_event)
    return jsonify({"message": "Event added successfully!"})

# ---------------------------------------
# Routes for `faculty` collection
# ---------------------------------------

@app.route('/faculty/<string:faculty_name>', methods=['GET'])
def get_faculty_by_name(faculty_name):
    # Search in the database using "name" instead of "_id"
    faculty = mongo.db.faculty.find_one({"name": {"$regex": f"^{faculty_name}$", "$options": "i"}})  # Case-insensitive match

    if faculty:
        faculty['_id'] = str(faculty['_id'])  # Convert ObjectId to string
        return jsonify(faculty)
    else:
        return jsonify({"error": "Faculty member not found"}), 404

@app.route('/add-faculty', methods=['POST'])
def add_faculty():
    new_faculty = request.json
    mongo.db.faculty.insert_one(new_faculty)
    return jsonify({"message": "Faculty member added successfully!"})

# ---------------------------------------
# Routes for `department` collection
# ---------------------------------------

@app.route('/departments/<string:dept_id>', methods=['GET'])
def get_department_by_id(dept_id):
    """Fetch department info by id."""
    department = mongo.db.department.find_one({"_id": dept_id.upper()})  # Convert dept_id to uppercase for case insensitivity
    if department:
        department['_id'] = str(department['_id'])  # Convert ObjectId to string if necessary
        return jsonify(department)
    else:
        return jsonify({"error": f"Department {dept_id} not found"}), 404

@app.route('/add-department', methods=['POST'])
def add_department():
    new_department = request.json
    mongo.db.department.insert_one(new_department)
    return jsonify({"message": "Department added successfully!"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
