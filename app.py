#!/bin/env python
# coding: utf-8

"""
Basic flask REST API-app to, thanks to
http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

$ git clone (url) testflask
$ cd testflask
$ virtualenv .
$ source ./bin/activate
$ pip install flask
$ pip install flash-httpauth
$ chmod +x app.py
$ ./app.py

$ curl -u test:demo -i http://localhost:5000/api/v1.0/tasks/

# or, using https://github.com/jakubroztocil/httpie
$ http -a test:demo http://localhost:5000/api/v1.0/tasks/

"""


from flask import Flask, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth


app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()


tasks = [
    {
        'id': 1,
        'title': u"Buy stuff",
        "description": u"Milk, Watermelon, Protein",
        "done": False,
    },
    {
        'id': 2,
        'title': u"Do a barell roll",
        "description": u"Do a yoba roll, and then flip it biyatch!",
        "done": False,
    },
]


@auth.get_password
def get_password(username): # LOL
    if username == "test":
        return "demo"
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': "Unathorized access"}), 401)


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], 
                    _external=True)
        else:
            new_task[field] = task[field]

    return new_task


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': "Not found"}), 404)


@app.route('/api/v1.0/tasks/', methods=["GET", "POST"])
@auth.login_required
def tasks_index():
    if request.method == "GET":
        return jsonify({'tasks': map(make_public_task, tasks)})
    if request.method == "POST":
        if not request.json or not 'title' in request.json:
            abort(400)
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'done': False,
        }
        tasks.append(task)
        return jsonify({'task': task}), 201


@app.route("/api/v1.0/tasks/<int:task_id>", methods=["GET", "PUT", "DELETE"])
@auth.login_required
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)

    if request.method == "GET":
        return jsonify({'task': task[0] })
    elif request.method == "PUT":
        if not request.json:
            abort(400)
        fields_with_types = [
                ('title', unicode),
                ('description', unicode),
                ('done', bool)
            ]

        for f, t in fields_with_types:
            if f in request.json and type(request.json[f]) is not t:
                abort(400)

        for f, _ in fields_with_types:
            task[0][f] = request.json.get(f, task[0][f])

        return jsonify({'task': task[0] })
    elif request.method == "DELETE":
        tasks.remove(task[0])
        return jsonify({'result': True})


if __name__ == "__main__":
    app.run(debug=True)
