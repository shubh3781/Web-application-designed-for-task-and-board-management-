#from crypt import methods
from random import getrandbits
from google.cloud import datastore
import google.oauth2.id_token
from flask import Flask, render_template, request,redirect,session
from google.auth.transport import requests
from datetime import datetime as dt

app = Flask(__name__)
app.secret_key = 'super secret key'
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

def retrieveUserInfo(email):
    entity_key = datastore_client.key('UserInfo', email)
    entity = datastore_client.get(entity_key)
    return entity

def retrieveBoardInfo(id):
    entity_key = datastore_client.key('BoardInfo', id)
    entity = datastore_client.get(entity_key)
    return entity

def retrieveTaskInfo(id):
    entity_key = datastore_client.key('TaskInfo', id)
    entity = datastore_client.get(entity_key)
    return entity

def retrieveAllUsers():
    return list(datastore_client.query(kind='UserInfo').fetch())

def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'board_key_list':[]
    })
    datastore_client.put(entity)


def createBoardInfo(title):
    id = getrandbits(63)
    entity_key = datastore_client.key('BoardInfo', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'title':title,
        'created_by':session['email'],
        'task_key_list':[],
        'users_email_list':[]
    })
    datastore_client.put(entity)
    current_user = retrieveUserInfo(session['email'])
    current_user_boards = current_user['board_key_list']
    current_user_boards.append(id)
    current_user.update({
        'board_key_list':current_user_boards
    })
    datastore_client.put(current_user)

def createTaskInfo(title,due_date,due_time,board_id):
    id = getrandbits(63)
    entity_key = datastore_client.key('TaskInfo', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'title':title,
        'due_date':due_date,
        'due_time':due_time,
        'is_assigned':False,
        'assigned_to':None,
        'complete_time':None,
        'complete_date':None,
        'red_color':False
    })
    datastore_client.put(entity)
    current_board = retrieveBoardInfo(board_id)
    current_board_tasks = current_board['task_key_list']
    current_board_tasks.append(id)
    current_board.update({
        'task_key_list':current_board_tasks
    })
    datastore_client.put(current_board)

def removeTask(task_id,board_id):
    entity_key = datastore_client.key('TaskInfo', task_id)
    datastore_client.delete(entity_key)
    board = retrieveBoardInfo(board_id)
    task_key_list = board['task_key_list']
    task_key_list.remove(task_id)
    board.update({
        'task_key_list':task_key_list
    })
    datastore_client.put(board)

@app.route('/assign_task',methods=['post'])
def assign_task():
    board_key = int(request.form['board_key'])
    task_key = int(request.form['task_key'])
    assigned_to = request.form['assigned_to']
    task = retrieveTaskInfo(task_key)
    task.update({
        'assigned_to':assigned_to,
        'is_assigned':True,
        'red_color':False
    })
    datastore_client.put(task)
    return redirect('/display_board/'+str(board_key))

@app.route('/add_task',methods=['post'])
def add_task():
    title = request.form['title']
    date_time = request.form['due_date_time']
    board_key = int(request.form['board_key'])
    board = retrieveBoardInfo(board_key)
    add = True
    for key in board['task_key_list']:
        if retrieveTaskInfo(key)['title']==title:
            add = False
            break
    if not add: return "Already Exists"
    else:
        createTaskInfo(title,date_time.split('T')[0],date_time.split('T')[1],board_key)
        return redirect('/display_board/'+str(board_key))

@app.route('/mark_completed',methods=['post'])
def mark_completed():
    board_key = int(request.form['board_key'])
    task_key = int(request.form['task_key'])
    task = retrieveTaskInfo(task_key)
    now = dt.now().strftime("%Y-%m-%d %H:%M")
    cur_date = now.split(' ')[0]
    cur_time = now.split(' ')[1]
    task.update({
        'complete_time':cur_time,
        'complete_date':cur_date
    })
    datastore_client.put(task)
    return redirect('/display_board/'+str(board_key))

@app.route('/edit_task',methods=['post'])
def edit_task():
    board_key = int(request.form['board_key'])
    task_key = int(request.form['task_key'])
    title = request.form['title']
    date_time = request.form['due_date_time']
    board = retrieveBoardInfo(board_key)
    add = True
    for key in board['task_key_list']:
        if key==task_key:continue
        if retrieveTaskInfo(key)['title']==title:
            add = False
            break
    if not add: return "Already Exists"
    else:
        task = retrieveTaskInfo(task_key)
        task.update({
            'title':title,
            'due_date':date_time.split('T')[0],
            'due_time':date_time.split('T')[1]
        })
        datastore_client.put(task)
        return redirect('/display_board/'+str(board_key))

@app.route('/delete_task',methods=['post'])
def delete_task():
    board_key = int(request.form['board_key'])
    task_key = int(request.form['task_key'])
    removeTask(task_key,board_key)
    return redirect('/display_board/'+str(board_key))

@app.route('/rename_board',methods=['post'])
def rename_board():
    board_key = int(request.form['board_key'])
    title = request.form['title']
    board = retrieveBoardInfo(board_key)
    board.update({
        'title':title
    })
    datastore_client.put(board)
    return redirect('/')

@app.route('/remove_user',methods=['post'])
def remove_user():
    board_key = int(request.form['board'])
    email = request.form['email']
    print(email)
    board = retrieveBoardInfo(board_key)
    users_email_list = board['users_email_list']
    users_email_list.remove(email)
    board.update({'users_email_list':users_email_list})
    datastore_client.put(board) # update board
    user = retrieveUserInfo(email)
    board_key_list = user['board_key_list']
    board_key_list.remove(board_key)
    user.update({'board_key_list':board_key_list})
    datastore_client.put(user)  # update user
    task_key_list = board['task_key_list']
    for key in task_key_list:
        task = retrieveTaskInfo(key)
        if task['assigned_to']==email:
            task.update({
                'assigned_to':None,
                'is_assigned':False,
                'red_color':True
            })
            datastore_client.put(task)
    return redirect('/display_board/'+str(board_key))

@app.route('/add_board_to_db',methods=['post'])
def add_board_to_db():
    createBoardInfo(request.form['title'])
    return redirect('/')

@app.route('/remove_board',methods=['post'])
def remove_board():
    board_key = int(request.form['board_key'])
    entity_key = datastore_client.key('BoardInfo', board_key)
    datastore_client.delete(entity_key)
    user = retrieveUserInfo(session['email'])
    board_key_list = user['board_key_list']
    board_key_list.remove(board_key)
    user.update({
        'board_key_list':board_key_list
    })
    datastore_client.put(user)
    return redirect('/')


@app.route('/invite_user',methods=['post'])
def invite_user():
    email = request.form['email']
    board_key = int(request.form['board'])
    board = retrieveBoardInfo(board_key)
    users_email_list = board['users_email_list']
    users_email_list.append(email)
    board.update({
        'users_email_list':users_email_list
    })
    user = retrieveUserInfo(email)
    board_key_list = user['board_key_list']
    board_key_list.append(board_key)
    user.update({
        'board_key_list':board_key_list
    })
    datastore_client.put(user)
    datastore_client.put(board)
    return redirect('/display_board/'+str(board_key))

def showBoard(id):
    board = retrieveBoardInfo(id)
    task_keys = board['task_key_list']
    tasks = []
    on_board_users = board['users_email_list']
    users = []
    all_users = retrieveAllUsers()
    for key in task_keys:
        tasks.append(retrieveTaskInfo(key))
    for user in all_users:
        if user['email'] not in on_board_users and user['email']!=board['created_by']:users.append(user)
    total = len(tasks)
    active = completed = completed_today = 0
    now = dt.now().strftime("%Y-%m-%d")
    for task in tasks:
        if task['complete_date']:
            completed+=1
            if task['complete_date']==now:
                completed_today+=1
        else:
            active+=1
    msg = "Total: "+str(total)+", Active: "+str(active)+", Completed: "+str(completed)+", Completed Today: "+str(completed_today)

    return render_template('display_board.html',board=board,tasks=tasks,users=users,msg = msg)

@app.route('/display_board/<int:id>',methods=['get'])
def display_board(id):
    if not session['email']:
        session['name'] = None
        session['email'] = None
        return "Please login first"
    else:
        return showBoard(id)

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    boards = []
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims['email'])
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims['email'])
            board_keys = user_info['board_key_list']
            for key in board_keys:
                boards.append(retrieveBoardInfo(key))

            session['name'] = claims['name']
            session['email'] = claims['email']
        except ValueError as exc:
            error_message = str(exc)
    else:
        session['name'] = None
        session['email'] = None
    return render_template('index.html', error_message=error_message,boards = boards)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
