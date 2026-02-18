from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"
@app.route('/create_account', methods = ['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if not username or not password:
            error = 'Username and password are required.'
            return render_template('create_account.html', error=error)
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, role)
            )
            conn.commit()
            session['authentifie'] = True
            redirect(url_for('lecture'))
        except sqlite3.IntegrityError:
            conn.rollback()
            error = 'Username already exists. Please choose another one.'
            return render_template('create_account.html', error=error)
        finally:
            conn.close()
    return render_template('create_account.html', error=None)
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, password, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            db_username, db_password, db_role = user
            if db_password == password:
                session['authentifie'] = True
                return redirect(url_for('lecture'))

        return render_template('formulaire_authentification.html', error = True)
    return render_template('formulaire_authentification.html', error = False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement


@app.route('/fiche_nom', methods=['GET', 'POST'])
def recherche_client():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    if request.method == 'GET':
        return render_template('fiche_nom.html')


    nom = request.form['nom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour chercher les clients avec le nom donné
    cursor.execute('SELECT * FROM clients WHERE nom = ?;', (nom,))
    test = cursor.fetchall()
    conn.close()
    if not test:
        return render_template('fiche_nom.html', error=True)
    else:
        return render_template('read_data.html', data=test)

@app.route('/formulaire_taches', methods=['GET', 'POST'])
@app.route('/new-task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form.get('description', '')
        date_echeance = request.form['date_echeance']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO taches (titre, description, date_echeance) VALUES (?, ?, ?)',
            (titre, description, date_echeance)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('read_tasks'))
    else:
        return render_template('formulaire_tache.html')

@app.route('/affiche_taches')
def read_tasks():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM taches;')
    taches = cursor.fetchall()
    conn.close()
    return render_template('affiche_taches.html', taches=taches)

@app.route('/supprimer/<int:tache_id>', methods=['POST', 'GET'])
def supprimer_tache(tache_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM taches WHERE id = ?', (tache_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('read_tasks'))

@app.route('/liste', methods=['GET', 'POST'])
def liste():
    import sqlite3
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Récupération titre, description et échéance [cite: 9, 10, 13]
        cursor.execute('INSERT INTO taches (titre, desc, date) VALUES (?, ?, ?)',
                       (request.form['t'], request.form['d'], request.form['e']))
        conn.commit()

    cursor.execute('SELECT * FROM taches')
    taches = cursor.fetchall()
    conn.close()
    return render_template('affiche taches.html', taches=taches)
if __name__ == "__main__":
  app.run(debug=True)
