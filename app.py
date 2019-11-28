from flask import Flask, render_template, request, json, redirect, session, flash, url_for
from flask_toastr import Toastr
from werkzeug.security import check_password_hash
from SQLConn import MSQLConn
from User import SimpleUser
from flask_socketio import SocketIO, join_room, leave_room
import sys

app = Flask(__name__)
app.secret_key = 'secretkey'
mysql = MSQLConn(app)

toastr = Toastr(app)

socketio = SocketIO(app)


@app.route("/")
def main():
    if session.get('user'):
        return redirect(url_for('home'))
    else:
        return render_template('index.html')


@app.route('/showSignUp')
def show_sign_up():
    return render_template('signup.html')


@app.route('/showSignIn')
def show_sign_in():
    if session.get('user'):
        return redirect(url_for('home'))
    else:
        return render_template('signin.html')


@app.route('/getRooms')
def get_rooms():
    return json.dumps(mysql.get_rooms())


@app.route('/Room/<room_name>')
def room(room_name):
    session['room'] = room_name
    return render_template('showroom.html')


@socketio.on('disconnect')
def on_disconnect():
    json_msg = {
        'message': 'rozłączył/a się!',
        'user_name': session['user_name']
    }
    socketio.emit('my response', json_msg, room=session['room'])


@socketio.on('join')
def on_join(data):
    session['room'] = data['room_name']
    join_room(session['room'])
    json_msg = {
        'message': 'dołączył/a do pokoju!',
        'user_name': session['user_name']
    }
    # mysql.join_room(session['user'], session['room'])
    socketio.emit('my response', json_msg, room=session['room'])


@socketio.on('leave')
def on_leave(data):
    leave_room(session['room'])
    json_msg = {
        'message': 'opuścił/a pokój!',
        'user_name': session['user_name']
    }
    socketio.emit('my response', json_msg, room=session['room'])
    session['room'] = ''
    # mysql.clear_joined_room(session['user'])


@socketio.on('my event')
def handle_my_custom_event(json_obj, methods=['GET', 'POST']):
    json_obj['user_name'] = session['user_name']
    print('received my event: ' + str(json_obj))
    socketio.emit('my response', json_obj, room=session['room'])


@app.route('/Home/<room_name>')
def show_spec_room(room_name):
    return redirect(url_for('room', room_name=room_name))


@app.route('/signUp', methods=['POST', 'GET'])
def sign_up():
    tmp_user = SimpleUser(0, request.form['inputEmail'], request.form['inputName'], request.form['inputPassword'])
    if tmp_user.have_valid_data:
        if len(tmp_user.name) > 45:
            flash('Nazwa wyświetlana użytkownika nie może przekraczać 45 znaków!', 'warning')
        elif len(tmp_user.login) > 45:
            flash('Adres e-mail nie może przekraczać 45 znaków!', 'warning')
        elif mysql.have_user_with_email(tmp_user.login):
            flash('Użytkownik z podanym adresem email już istnieje', 'warning')
        elif mysql.have_user_with_name(tmp_user.name):
            flash('Użytkownik o podanej nazwie już istnieje', 'warning')
        elif mysql.add_new_user(tmp_user):
            flash('Dodano nowego użytkownika', 'success')
        else:
            flash('Błąd wewnętrzny podczas dodawania użytkownika', 'error')
        return redirect(url_for('show_sign_up'))


@app.route('/createRoom')
def create_room():
    return render_template('createRoom.html')


@app.route('/Home')
def home():
    return render_template('home.html')


@app.route('/logout')
def logout():
    # mysql.clear_joined_room(session['user'])
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
def add_room():
    _title = request.form['inputTitle']
    if (_title is None) or (_title == ''):
        flash('Wprowadź poprawną nazwę pokoju', 'warning')
    elif len(_title) > 45:
        flash('Nazwa pokoju nie może przekraczać 45 znaków', 'warning')
    else:
        if mysql.have_room_with_title(_title):
            flash('Pokój o takiej nazwie już istnieje', 'warning')
        elif mysql.create_room(_title):
            flash('Stworzono nowy pokój', 'success')
            return redirect(url_for('home'))
        else:
            flash('Błąd wewnętrzny, nie można stworzyć pokoju', 'error')
    return redirect(url_for('create_room'))


@app.route('/Login', methods=['POST'])
def do_login():
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    if mysql.have_user_with_email(_username):
        tmp_user = mysql.get_user_with_login(_username)
        if check_password_hash(tmp_user.password, _password):
            session['logged_in'] = True
            session['user'] = tmp_user.us_id
            session['user_name'] = tmp_user.name
            return redirect(url_for('home'))
        else:
            flash('Błędny adres e-mail lub hasło', 'warning')
    else:
        flash('Błędny adres e-mail lub hasło', 'warning')
    return redirect(url_for('show_sign_in'))


if __name__ == "__main__":
    def_host = '192.168.0.197'
    def_port = 5000
    def_debug_en = False
    if len(sys.argv) > 1:
        def_host = str(sys.argv[1])
    if len(sys.argv) > 2:
        def_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        def_debug_en = bool(sys.argv[3])
    socketio.run(app, def_host, def_port, debug=def_debug_en)
