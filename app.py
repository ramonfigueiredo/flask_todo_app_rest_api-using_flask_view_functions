from flask import Flask, jsonify, abort, make_response, request, url_for


app = Flask(__name__)


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruits, Meat', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]


'''
All we are doing here is taking a task from our database and creating a new task 
that has all the fields except id, which gets replaced with another field called uri, 
generated with Flask's url_for.

For example: When we return the list of tasks we pass them through this function 
before sending them to the client.

curl -i http://localhost:5000/todo/api/v1.0/tasks

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 405
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 18:43:21 GMT

{
  "tasks": [
    {
      "description": "Milk, Cheese, Pizza, Fruits, Meat", 
      "done": false, 
      "title": "Buy groceries", 
      "uri": "http://localhost:5000/todo/api/v1.0/tasks/1"
    }, 
    {
      "description": "Need to find a good Python tutorial on the web", 
      "done": false, 
      "title": "Learn Python", 
      "uri": "http://localhost:5000/todo/api/v1.0/tasks/2"
    }
  ]
}
'''
def make_public_task(task):
  new_task = {}
  for field in task:
    if field == 'id':
      new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
    else:
      new_task[field] = task[field]
  return new_task


'''
GET: Retrieve list of tasks


To test: 

curl -i http://localhost:5000/todo/api/v1.0/tasks

OUTPUT:

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 315
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 15:36:15 GMT

{
  "tasks": [
    {
      "description": "Milk, Cheese, Pizza, Fruits, Meat", 
      "done": false, 
      "id": 1, 
      "title": "Buy groceries"
    }, 
    {
      "description": "Need to find a good Python tutorial on the web", 
      "done": false, 
      "id": 2, 
      "title": "Learn Python"
    }
  ]
}
'''
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
	return jsonify({'tasks': [make_public_task(task) for task in tasks]})


'''
GET: Retrieve a task by id 


To test:

curl -i http://localhost:5000/todo/api/v1.0/tasks/1

OUTPUT:

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 140
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 15:36:54 GMT

{
  "task": {
    "description": "Milk, Cheese, Pizza, Fruits, Meat", 
    "done": false, 
    "id": 1, 
    "title": "Buy groceries"
  }
}

curl -i http://localhost:5000/todo/api/v1.0/tasks/3

OUTPUT:

HTTP/1.0 404 NOT FOUND
Content-Type: application/json
Content-Length: 27
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 15:37:19 GMT

{
  "error": "Not found"
}
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return jsonify({'task': make_public_task(task[0])})

'''
Return the 404 error in json format
'''
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)	


'''
POST: Create a new task


To test: 

curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks

OUTPUT:

HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 105
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 15:38:33 GMT

{
  "task": {
    "description": "", 
    "done": false, 
    "id": 3, 
    "title": "Read a book"
  }
}
'''
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1,
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done': False
	}
	tasks.append(task)
	return jsonify({'task': [make_public_task(task) for task in tasks]}), 201


'''
PUT: Update an existing task


To test:

curl -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/v1.0/tasks/2

OUTPUT:

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 151
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 15:39:07 GMT

{
  "task": {
    "description": "Need to find a good Python tutorial on the web", 
    "done": true, 
    "id": 2, 
    "title": "Learn Python"
  }
}
'''

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({'task': make_public_task(task[0])})


'''
DELETE: Delete a task


To test:

curl -X DELETE http://localhost:5000/todo/api/v1.0/tasks/2

OUTPUT

{
  "result": true
}
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True})


if __name__ == '__main__':
	app.run(debug=True)
