from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET','POST'])
def post():
    if request.method == "POST":
        title = request.json['title']
        content = request.json['content']
        if title == "" or content == "":
            return "", 400
        if not POSTS:
            new_id = 1
        else:
            current_ids = [post['id'] for post in POSTS]
            new_id = max(current_ids) + 1
        new_post = {
            "id": new_id,
            "title": title,
            "content": content
        }
        POSTS.append(new_post)
        return jsonify(new_post), 201
    else:
        return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
