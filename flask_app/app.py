from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS  #  Import CORS

app = Flask(__name__)
CORS(app)  #  Enable CORS for all routes

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
# Routes for events collection
# ---------------------------------------

@app.route('/add-event', methods=['POST'])
def add_event():
    new_event = request.json
    mongo.db.events.insert_one(new_event)
    return jsonify({"message": "Event added successfully!"})

@app.route('/events/<string:department_name>', methods=['GET'])
def get_event_info(department_name):
    """Fetch all events for the given department name."""
    events = list(mongo.db.events.find({"department": {"$regex": department_name, "$options": "i"}}))  # Fetch all matching events
    
    for event in events:
        event['_id'] = str(event['_id'])  # Convert ObjectId to string

    if events:
        return jsonify(events)  # Return all events as a list
    else:
        return jsonify({"error": "No events found for this department"}), 404

# ---------------------------------------
# Routes for faculty collection
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
# Routes for department collection
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

    # Normalize input: Remove prefixes, honorifics, and dots
    normalized_name = (
        faculty_name.lower()
        .replace("dr ", "")
        .replace("prof ", "")
        .replace("mam", "")
        .replace("sir", "")
        .replace(".", "")
        .strip()
    )

    print(f"Normalized faculty lookup: {normalized_name}")  # Debugging log

    # Find faculty ID in the mapping
    for key in faculty_mapping.keys():
        print(f"Checking if '{normalized_name}' matches '{key.lower()}'")  # Debugging log
        if normalized_name in key.lower() or key.lower() in normalized_name:
            faculty_id = faculty_mapping[key]
            faculty = mongo.db.faculty.find_one({"_id": faculty_id})
            if faculty:
                faculty['_id'] = str(faculty['_id'])  # Convert ObjectId to string
                return jsonify(faculty)
            else:
                return jsonify({"error": "Faculty member not found"}), 404

    return jsonify({"error": f"Faculty {normalized_name} not found in mapping"}), 404

# Run the app
if __name__ == "__main__":  # Correct this line
    app.run(debug=True, port=5000)
