from flask import Flask, render_template, request, redirect, make_response
from string import Template
import requests
import os
import json

app = Flask(__name__)


@app.route('/')
def home(): 
	if('sillyauth' in request.cookies):	
		res = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies = request.cookies)
		todos = json.loads(res.text)
		if (res.status_code == 200):
			return render_template('index.html', todos = todos)
	else:
		return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
	username = Template('{"username": "$username"}').safe_substitute(username = request.form['username'])
	if(username == ""):
		message = "error, enter username"
		return render_template('login.html')
	else:
		res = requests.post('https://hunter-todo-api.herokuapp.com/auth', data = username)
		if (res.status_code == 200):
			cookie = json.loads(res.text)
			resp = make_response(redirect('/'))
			resp.set_cookie('sillyauth', cookie['token'])
			return resp 
	
@app.route('/register', methods = ['POST', 'GET'])
def register():
	if request.method == 'POST':
		username = Template('{"username": "$username"}').safe_substitute(username = request.form['username'])
		requests.post('https://hunter-todo-api.herokuapp.com/user', data = username)
		return redirect('/')
	else:
		return render_template('register.html')	

@app.route('/logout')
def logout():
	resp = make_response(redirect('/'))
	resp.set_cookie('sillyauth', expires=0)
	return resp
	
@app.route('/todo', methods=['POST'])
def add():
	if request.form['newtask']:
		newtask = Template('{"content": "$task" }').safe_substitute(task = request.form['newtask'])
		requests.post('https://hunter-todo-api.herokuapp.com/todo-item', data = newtask, cookies = request.cookies)
	return redirect('/')

@app.route('/delete/<elem>')
def delete(elem):
	requests.delete('https://hunter-todo-api.herokuapp.com/todo-item/' + elem , cookies = request.cookies)
	return redirect('/')
	
@app.route('/toggle/<elem>/<status>')
def toggle(elem, status):
	if(status == "True"):
		res = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/' + elem , data = '{"completed": false}', cookies=request.cookies)
		return redirect('/')
	if(status == "False"):
		res = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/' + elem , data = '{"completed": true}', cookies=request.cookies)
		return redirect('/')

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, threaded=True, debug=True)