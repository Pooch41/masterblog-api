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

@app.route('/api/posts/<id>', methods = ['DELETE', 'PUT'])
def modify_post(id):
    if request.method == 'DELETE':
        current_ids = [post['id'] for post in POSTS]
        post_id = int(id)
        if post_id not in current_ids:
            return "", 404
        else:
            for post in POSTS:
                if post_id == post['id']:
                    POSTS.remove(post)
                    break
            confirmation = {"message": f"Post with id {post_id} has been deleted successfully."}
            return jsonify(confirmation), 200
    else:
        title = request.json['title']
        content = request.json['content']
        current_ids = [post['id'] for post in POSTS]
        post_id = int(id)
        if post_id not in current_ids:
            return "", 404

        modified_post = None
        for post in POSTS:
            if post_id == post['id']:
                if title != "":
                    post['title'] = title
                if content != "":
                    post['content'] = content
                modified_post = post
                break


        return jsonify(modified_post), 200




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
