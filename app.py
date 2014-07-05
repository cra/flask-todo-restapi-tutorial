#!/bin/env python
# coding: utf-8

from flask import Flask, jsonify, abort, make_response, request, url_for


app = Flask(__name__)


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


ACCESS_URL = "/api/v1.0/tasks/<int:task_id>"

@app.route(ACCESS_URL, methods=["GET", "PUT", "DELETE"])
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
