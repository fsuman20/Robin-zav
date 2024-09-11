#==========4. RUN API.PY (USE POSTMAN TO TEST THE API)================
from flask import Flask, request, jsonify
from chat import initialize_index, query_index
from config import FLASK_HOST, FLASK_PORT
from flask_cors import CORS

app = Flask(__name__)
CORS(app) #Cors

index = initialize_index()

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Handles the query by checking if the index is initialized, retrieving the query from the request data,
    and processing the query using the query_index function.
    Returns:
        A JSON response containing the result of the query.
    """
    if not index:
        return jsonify({"error": "Index not initialized"}), 500

    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400

    query = data['query'] 
    response = query_index(index, query)

    if response is None:
        return jsonify({"error": "Failed to process query"}), 500

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)