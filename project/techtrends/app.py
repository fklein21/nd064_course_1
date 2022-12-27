import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get a post using its ID
def get_post_count():
    connection = get_db_connection()
    post = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()
    return post

# Function to check if the table exists in the db (source: (1))
def check_table_exists(table_name):
    connection = get_db_connection()
    tc = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table_name,)).fetchone()
    connection.close()
    return tc

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    app.logger.info('Main request successful.')
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define the health/status route of the web application
@app.route('/healthz')
def status():
    app.logger.info('Health request successful.')
    if check_table_exists("posts") is not None:
        response = app.response_class(
                response=json.dumps({"result":"OK - healthy"}),
                status=200,
                mimetype='application/json'
        )
    else:
        response = app.response_class(
                response=json.dumps({"result":"Unhealthy - Database error: No table posts"}),
                status=500,
                mimetype='application/json'
        )
    return response

# Define the metrics route of the web applciation
@app.route('/metrics')
def metrics():
    app.logger.info('Metrics request successful.')
    post_count = get_post_count()[0]
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"post_count":post_count}}),
            status=200,
            mimetype='application/json'
    )
    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    app.logger.info('Post request successful.')
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About request successful.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    app.logger.info('Create request successful.')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        app.logger.info('Request content: '+title)
        app.logger.info('Request content: '+content)

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # (2)
    logging.basicConfig(format=format, level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')



# Content taken (and modified) from this sources
# (1) - https://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
# (2) - https://java2blog.com/log-to-stdout-python/


