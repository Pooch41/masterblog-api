from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
from operator import itemgetter

def load_posts():
    """Opens and returns the loaded JSON file."""
    with open('posts.json', 'r') as file:
        posts = json.load(file)
    return posts

def save_posts(posts):
    """Saves the json file changes."""
    with open('posts.json', 'w') as file:
        json.dump(posts, file, indent=4)


def sort_posts_list(posts, sort_by='date', sort_order='desc'):
    """Sorts the list of posts based on the given key and order."""
    valid_keys = ['author', 'content', 'date', 'title', 'id']
    if sort_by not in valid_keys:
        sort_by = 'date'
    reverse_sort = sort_order.lower() == 'desc'
    try:
        posts.sort(key=itemgetter(sort_by), reverse=reverse_sort)
    except KeyError:
        posts.sort(key=itemgetter('id'))
    return posts

app = Flask(__name__)
CORS(app)

@app.route('/api/posts', methods=['GET','POST'])
def post():
    if request.method == "POST":
        POSTS = load_posts()

        title = request.json.get('title','')
        content = request.json.get('content', '')
        author = request.json.get('author', '')
        date = request.json.get('date', '')

        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Date must be in YYYY-MM-DD format."}), 400

        if not title or not content or not author or not date:
            return "", 400

        if not POSTS:
            new_id = 1
        else:
            current_ids = [post['id'] for post in POSTS]
            new_id = max(current_ids) + 1
        new_post = {
            "id": new_id,
            "title": title,
            "content": content,
            "author": author,
            "date": date
        }
        POSTS.append(new_post)

        save_posts(POSTS)
        return jsonify(new_post), 201

    else:
        POSTS = load_posts()
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'desc')
        sorted_posts = sort_posts_list(POSTS, sort_by, sort_order)
        return jsonify(sorted_posts), 200


@app.route('/api/posts/<id>', methods = ['DELETE', 'PUT'])
def modify_post(id):
    if request.method == 'DELETE':
        POSTS = load_posts()
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
            save_posts(POSTS)
            return jsonify(confirmation), 200
    else:
        if 'date' in request.json:
            return jsonify({"error": "Modifying the 'date' field is not allowed."}), 400

        POSTS = load_posts()
        title = request.json.get('title', '')
        content = request.json.get('content', '')
        author = request.json.get('author', '')

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
                if author != "":
                    post['author'] = author

                modified_post = post
                break

        save_posts(POSTS)
        return jsonify(modified_post), 200


@app.route('/api/search', methods=['GET'])
def search_post():
    POSTS = load_posts()
    search_param = request.args.get('query')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    if not search_param:
        return jsonify(sort_posts_list(POSTS, sort_by, sort_order)), 200
    try:
        search_by, search_query = search_param.split(':', 1)
    except ValueError:
        return jsonify({"error": "Invalid search query format. Must be 'field:term'."}), 400

    valid_fields = ['title', 'content', 'author', 'date']
    if search_by.lower() not in valid_fields:
        return jsonify({"error": f"Invalid search field: {search_by}"}), 400

    search_by = search_by.lower()
    search_query = search_query.lower()

    found_posts = []
    for post in POSTS:
        if search_by in post and search_query in str(post[search_by]).lower():
            found_posts.append(post)

    sorted_posts = sort_posts_list(found_posts, sort_by, sort_order)

    return jsonify(sorted_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
