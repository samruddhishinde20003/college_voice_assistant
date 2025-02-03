from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

# Create Flask app
app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/voice_assistant"
mongo = PyMongo(app)

# Define Faculty Mapping
faculty_mapping = {
    "rajesh": "CSE_FAC001",
    "geeta": "CSE_FAC002",
    "yerriswamy": "CSE_FAC003",
    "gopal": "ECE_FAC001",
    "manu": "ECE_FAC002",
    "rajeshwari": "ECE_FAC003",
    "sharanabasappa": "ME_FAC001",
    "anand": "ME_FAC002",
    "veerabhadrayya": "ME_FAC003"
}

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

@app.route('/events/<string:department_name>', methods=['GET'])
def get_event_info(department_name):
    """Fetch event info based only on department name."""
    # Perform a case-insensitive search for events based on the department name
    event = mongo.db.events.find_one({"department": {"$regex": department_name, "$options": "i"}})
    
    if event:
        event['_id'] = str(event['_id'])  # Convert ObjectId to string if necessary
        return jsonify(event)
    else:
        return jsonify({"error": "Event not found for this department"}), 404

# ---------------------------------------
# Routes for `faculty` collection
# ---------------------------------------

@app.route('/faculty/<string:faculty_id>', methods=['GET'])
def get_faculty_by_id(faculty_id):
    faculty = mongo.db.faculty.find_one({"_id": faculty_id})  # Query by _id
    if faculty:
        faculty['_id'] = str(faculty['_id'])  # Convert ObjectId to string if needed
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

# ---------------------------------------
# Route for Faculty by Name Lookup (via Mapping)
# ---------------------------------------

@app.route('/faculty-name/<string:faculty_name>', methods=['GET'])
def get_faculty_by_name(faculty_name):
    """Look up faculty member by name (using faculty_mapping)."""
    # Use the faculty_mapping to get faculty_id by name
    faculty_id = faculty_mapping.get(faculty_name.lower())
    
    if faculty_id:
        faculty = mongo.db.faculty.find_one({"_id": faculty_id})
        if faculty:
            faculty['_id'] = str(faculty['_id'])  # Convert ObjectId to string if necessary
            return jsonify(faculty)
        else:
            return jsonify({"error": "Faculty member not found"}), 404
    else:
        return jsonify({"error": f"Faculty {faculty_name} not found in mapping"}), 404

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
