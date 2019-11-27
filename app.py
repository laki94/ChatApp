from flask import Flask, render_template, request, json, redirect, session, flash, url_for
from flask_toastr import Toastr
from werkzeug.security import check_password_hash
from SQLConn import MSQLConn
from User import SimpleUser
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
app.secret_key = 'secretkey'
mysql = MSQLConn(app)

toastr = Toastr(app)

socketio = SocketIO(app)


@app.route("/")
def main():
    if session.get('user'):
        return redirect('/userHome')
    else:
        return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/showSignIn')
def showSignIn():
    if session.get('user'):
        return redirect('/userHome')
    else:
        return render_template('signin.html')


@app.route('/getRooms')
def getRooms():
    return json.dumps(mysql.get_rooms())


@app.route('/Room/<room_name>')
def Room(room_name):
    return render_template('showroom.html')


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('join')
def on_join(data):
    username = session['user_name']
    session['room'] = data['room_name']
    join_room(session['room'])
    json_msg = {
        'message': 'dołączył/a do pokoju!',
        'user_name': session['user_name']
    }
    mysql.join_room(session['user'], session['room'])
    socketio.emit('my response', json_msg, callback=messageReceived(), room=session['room'])


@socketio.on('leave')
def on_leave(data):
    username = session['user_name']
    leave_room(session['room'])
    json_msg = {
        'message': 'opuścił/a pokój!',
        'user_name': session['user_name']
    }
    socketio.emit('my response', json_msg, callback=messageReceived(), room=session['room'])
    session['room'] = ''
    mysql.clear_joined_room(session['user'])


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    json['user_name'] = session['user_name']
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived, room=session['room'])


@app.route('/userHome/<room_name>')
def joinRoom(room_name):
    return redirect(url_for('Room', room_name=room_name))


@app.route('/signUp',methods=['POST', 'GET'])
def signUp():
    tmp_user = SimpleUser(request.form['inputName'], request.form['inputEmail'], request.form['inputPassword'])
    if tmp_user.have_valid_data:
        if mysql.have_user_with_email(tmp_user.login):
            flash('Użytkownik z podanym adresem email już istnieje')
        elif mysql.have_user_with_name(tmp_user.name):
            flash('Użytkownik o podanej nazwie już istnieje')
        elif mysql.add_new_user(tmp_user):
            flash('Dodano nowego użytkownika')
        else:
            flash('Błąd wewnętrzny podczas dodawania użytkownika')
        return redirect(url_for('showSignUp'))


@app.route('/createRoom')
def createRoom():
    return render_template('createRoom.html')


@app.route('/userHome')
def userHome():
    return render_template('userHome.html')


@app.route('/logout')
def logout():
    mysql.clear_joined_room(session['user'])
    session['logged_in'] = False
    session['user'] = 0
    session['user_name'] = ''
    session['room'] = ''
    session.pop('user', None)
    session.pop('logged_in', None)
    session.pop('user_name', None)
    session.pop('room', None)
    return redirect('/')


@app.route('/addRoom', methods=['POST'])
def addRoom():
    _title = request.form['inputTitle']
    if mysql.have_room_with_title(_title):
        flash('Pokój o takiej nazwie już istnieje')
    elif mysql.create_room(_title):
        flash('Stworzono nowy pokój')
        return redirect(url_for('userHome'))
    else:
        flash('Błąd wewnętrzny, nie można stworzyć pokoju')
    return redirect(url_for('createRoom'))


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    if mysql.have_user_with_email(_username):
        tmp_user = mysql.get_user_with_login(_username)
        if check_password_hash(tmp_user.password, _password):
            session['logged_in'] = True
            session['user'] = tmp_user.us_id
            session['user_name'] = tmp_user.name
            return redirect(url_for('userHome'))
        else:
            flash('Błąd wewnętrzny, nie można zweryfikować poprawności danych')
    else:
        flash('Nie znaleziono użytkownika o podanym adresie email')
    return redirect(url_for('showSignIn'))


if __name__ == "__main__":
   socketio.run(app, '192.168.0.197', 5000, debug=True)
    # app.run(host='192.168.0.197', debug=True)
