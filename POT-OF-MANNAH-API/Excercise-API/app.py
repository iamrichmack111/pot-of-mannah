from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'exercise.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

@app.route('/search', methods=['GET'])
def search():
    main_muscle = request.args.get('main_muscle', None)
    if not main_muscle:
        return jsonify({"error": "main_muscle parameter is required"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM exercises WHERE Main_muscle LIKE ?", ('%' + main_muscle + '%',))
    rows = cursor.fetchall()

    exercises = []
    for row in rows:
        exercises.append({
            "Exercise_Name": row["Exercise_Name"],
            "Equipment": row["Equipment"],
            "Variation": row["Variation"],
            "Utility": row["Utility"],
            "Mechanics": row["Mechanics"],
            "Force": row["Force"],
            "Preparation": row["Preparation"],
            "Execution": row["Execution"],
            "Target_Muscles": row["Target_Muscles"],
            "Synergist_Muscles": row["Synergist_Muscles"],
            "Stabilizer_Muscles": row["Stabilizer_Muscles"],
            "Antagonist_Muscles": row["Antagonist_Muscles"],
            "Dynamic_Stabilizer_Muscles": row["Dynamic_Stabilizer_Muscles"],
            "Main_muscle": row["Main_muscle"],
            "Difficulty": row["Difficulty"],
            "Secondary_Muscles": row["Secondary_Muscles"],
            "parent_id": row["parent_id"]
        })

    return jsonify(exercises), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')