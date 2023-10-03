from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import json
import uuid
from DataManager.json_data_manager import JSONDataManager


app = Flask(__name__)

json_data_manager = JSONDataManager('movies.json')


def generate_user_id():
    return str(uuid.uuid4())


def fetch_movie_info(movie_title, api_key='5eeb20d'):
    """
    Fetches movie information from the OMDB API based on the provided movie
    title.

    Args:
        movie_title (str): The title of the movie to search for on the OMDB
        API.

    Returns:
        dict or None: A dictionary containing movie information if the API
        request
        is successful and the movie is found. Returns None if the movie is not
        found
        or if there is an issue with the API request.

    Note:
        This function sends an HTTP GET request to the OMDB API with the
        provided movie title and API key. If the response status code is
        200 (OK), it parses the JSON response and returns a dictionary
        containing movie details.
        If the movie is not found or if there is an issue with the API request,
        it returns None.
        :param movie_title:
        :param api_key:
    """

    try:
        encoded_title = requests.utils.quote(movie_title)

        url = f'http://www.omdbapi.com/?t={encoded_title}&apikey={api_key}'

        response = requests.get(url)
        movie_details = response.json()

        if movie_details.get('Response') == 'True':
            movie_data = {
                'name': movie_details.get('Title'),
                'director': movie_details.get('Director'),
                'year': int(movie_details.get('Year')),
                'rating': float(movie_details.get('imdbRating'))
            }
            return movie_data
        else:
            return None
    except Exception as e:
        print(f"Error fetching movie info: {str(e)}")
        return None


@app.route('/')
def home():
    """Renders the home page.

    Returns:
        A rendered template of the home page.
    """
    return render_template('home.html')


@app.route('/users')
def list_users():
    """Renders a page listing all users.

    Returns:
        A rendered template of the users page, with all users passed
        to the template.
    """
    users = json_data_manager.list_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<user_id>')
def user_movies(user_id):
    """Renders a page showing all movies of a specific user.

    Args:
        user_id (str): The ID of the user.

    Returns:
        A rendered template of the user's movies page, with the user's
        ID and movies passed to the template.
    """
    movies = json_data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user_id=user_id, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form.get('name')
        error_message, user_name = json_data_manager.add_user(user_name)

        if error_message is not None:
            return render_template('add_user.html', error_message=error_message)

        return redirect(url_for('user_movies', user_id=user_name))

    return render_template('add_user.html')


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Handles the addition of a new movie to a specific user's list.

    Args:
        user_id (str): The ID of the user.

    Returns:
        JSON response indicating success or failure.

    Note:
        This route allows users to add a movie to their list by providing the
        movie title. It fetches additional movie details from the OMDB API
        and returns a JSON response indicating success or failure.
    """
    if request.method == 'POST':
        movie_title = request.form.get('name')

        movie_data = fetch_movie_info(movie_title)

        if movie_data:
            result = json_data_manager.add_movie(user_id, movie_title)

            if result is None:
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                error_message = result
        else:
            error_message = "Movie not found on OMDB"
            return render_template('add_movie.html', user_id=user_id,
                                   error_message=error_message)

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Renders a page to update a specific movie for a specific user and
    handles the submission of the form.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        If the form is submitted successfully, redirects to the user's
        movies page.
        Otherwise, renders the update movie page with the current movie data.
    """
    movie = json_data_manager.get_movie(user_id, movie_id)

    if request.method == 'POST':
        updated_movie = {
            'title': request.form.get('name'),  # Change 'title' to 'name'
            'director': request.form.get('director'),
            'year': int(request.form.get('year')),
            'rating': float(request.form.get('rating'))
        }
        json_data_manager.update_movie(user_id, movie_id, updated_movie)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', user_id=user_id,
                           movie=movie, movie_id=movie_id)


@app.route('/users/<user_id>/delete_movie/<movie_id>')
def delete_movie(user_id, movie_id):
    """Deletes a specific movie for a specific user and redirects
    to the user's movies page.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        Redirects to the user's movies page.
    """
    json_data_manager.delete_movie(user_id, movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """Renders a 404 page when a page is not found.

    Args:
        e (Exception): The exception that occurred.

    Returns:
        A rendered template of the 404 page, with a status code of 404.
    """
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
