from flask import Flask, render_template, request, json, redirect, session, flash, url_for
from flask_toastr import Toastr
from werkzeug.security import check_password_hash
from SQLConn import MSQLConn
from User import SimpleUser

app = Flask(__name__)
app.secret_key = 'secretkey'
mysql = MSQLConn(app)

toastr = Toastr(app)


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


@app.route('/userHome')
def userHome():
    return render_template('userHome.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('user', None)
    return redirect('/')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    if mysql.have_user_with_email(_username):
        tmp_user = mysql.get_user_with_login(_username)
        if check_password_hash(tmp_user.password, _password):
            session['logged_in'] = True
            return redirect(url_for('userHome'))
        else:
            flash('Błąd wewnętrzny, nie można zweryfikować poprawności danych')
    else:
        flash('Nie znaleziono użytkownika o podanym adresie email')
    return redirect(url_for('showSignIn'))


if __name__ == "__main__":
    app.run(host='192.168.0.197', debug=True)
