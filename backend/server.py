from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/status')
def status():
    print("✅ /api/status was hit")
    return jsonify({"status": "Student Hub API running"})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
