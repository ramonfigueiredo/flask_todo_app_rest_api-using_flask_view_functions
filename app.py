import six
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()


'''
In this case, the web service to only be accessible to username 'user1' 
and password 'password'.

The authentication extension gives us the freedom to choose which 
functions in the service are open and which are protected.

Use @auth.login_required choose which functions in the service are 
protected by user and password.
'''
@auth.get_password
def get_password(username):
  if username == 'user1':
    return 'password'
  return None


@auth.error_handler
def unauthorized():
  '''
  Return 403 instead of 401 to prevent browsers from displaying the default
  auth dialog
  '''
  return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
  '''
  Return the 400 error in json format
  '''
  return make_response(jsonify({'error': 'Bad request'}), 400)  


@app.errorhandler(404)
def not_found(error):
  '''
  Return the 404 error in json format
  '''
  return make_response(jsonify({'error': 'Not found'}), 404) 


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

For example, when we return the list of tasks we pass them through this function 
before sending them to the client.
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

curl -i http://localhost:5000/todo/api/v1.0/tasks -u user1:password

OUTPUT:

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 405
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 19:41:58 GMT

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
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
	return jsonify({'tasks': [make_public_task(task) for task in tasks]})


'''
GET: Retrieve a task by id 


To test:

curl -i http://localhost:5000/todo/api/v1.0/tasks/1 -u user1:password

OUTPUT:

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 185
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 19:46:33 GMT

{
  "task": {
    "description": "Milk, Cheese, Pizza, Fruits, Meat", 
    "done": false, 
    "title": "Buy groceries", 
    "uri": "http://localhost:5000/todo/api/v1.0/tasks/1"
  }
}

curl -i http://localhost:5000/todo/api/v1.0/tasks/3 -u user1:password

OUTPUT:

HTTP/1.0 404 NOT FOUND
Content-Type: application/json
Content-Length: 27
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 19:47:14 GMT

{
  "error": "Not found"
}
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return jsonify({'task': make_public_task(task[0])})


'''
POST: Create a new task


To test: 

curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks -u user1:password

OUTPUT:

HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 556
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 19:50:48 GMT

{
  "task": [
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
    }, 
    {
      "description": "", 
      "done": false, 
      "title": "Read a book", 
      "uri": "http://localhost:5000/todo/api/v1.0/tasks/3"
    }
  ]
}
'''
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1 if len(tasks) > 0 else 1,
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done': False
	}
	tasks.append(task)
	return jsonify({'task': make_public_task(task)}), 201


'''
PUT: Update an existing task


To test:

curl -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/v1.0/tasks/2 -u user1:password

OUTPUT:

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 196
Server: Werkzeug/0.15.5 Python/3.7.4
Date: Tue, 06 Aug 2019 19:51:54 GMT

{
  "task": {
    "description": "Need to find a good Python tutorial on the web", 
    "done": true, 
    "title": "Learn Python", 
    "uri": "http://localhost:5000/todo/api/v1.0/tasks/2"
  }
}
'''

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and \
        not isinstance(request.json['title'], six.string_types):
		abort(400)
	if 'description' in request.json and \
        not isinstance(request.json['description'], six.string_types):
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

curl -X DELETE http://localhost:5000/todo/api/v1.0/tasks/2 -u user1:password

OUTPUT

{
  "result": true
}
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True})


if __name__ == '__main__':
	app.run(debug=True)
