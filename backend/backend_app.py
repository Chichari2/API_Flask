from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def generate_new_id():
    if POSTS:
        return max(post['id'] for post in POSTS) + 1
    else:
        return 1


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    # Validate sort field
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400

    # Validate sort direction
    if sort_direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid sort direction. Must be 'asc' or 'desc'."}), 400

    sorted_posts = POSTS.copy()  # Copy the original list to avoid mutating it

    # Perform sorting if sort_field is provided
    if sort_field:
        reverse = (sort_direction == 'desc')
        sorted_posts = sorted(sorted_posts, key=lambda x: x[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200



@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Error handling for missing fields
    if not data or not 'title' in data or not 'content' in data:
        return jsonify({"error": "Both 'title' and 'content' fields are required."}), 400

    new_post = {
        "id": generate_new_id(),
        "title": data['title'],
        "content": data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = next((post for post in POSTS if post['id'] == id), None)

    # Error handling if the post does not exist
    if post is None:
        return jsonify({"error": f"Post with id {id} not found."}), 404

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    post = next((post for post in POSTS if post['id'] == id), None)

    if post is None:
        return jsonify({"error": f"Post with id {id} not found."}), 404

    # Update the post with the provided data, keeping old values if not provided
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])

    return jsonify(post), 200



@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    matching_posts = []

    for post in POSTS:
        title_matches = title_query in post['title'].lower() if title_query else False
        content_matches = content_query in post['content'].lower() if content_query else False

        if title_matches or content_matches:
            matching_posts.append(post)

    return jsonify(matching_posts), 200



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
