import json
import requests
from DataManager.data_manager_interface import DataManagerInterface


class JSONDataManager(DataManagerInterface):
    def __init__(self, json_file):
        """Initializes the JSONDataManager with a JSON file.
        Args:
            json_file (str): The path to the JSON file.
        """
        self.json_file = json_file

    def _load_data(self):
        """Loads data from the JSON file.
        Returns:
            list: The list of users from the JSON file.
        """
        with open(self.json_file, 'r') as file:
            data = json.load(file)
        return data['users']

    def _write_data(self, data):
        """Writes data to the JSON file.
        Args:
            data (list): The list of users to write to the JSON file.
        """
        with open(self.json_file, 'w') as file:
            json.dump({'users': data}, file)

    def list_all_users(self):
        """Returns a list of all users.
        Returns:
            list: The list of all users.
        """
        data = self._load_data()
        return data

    def add_user(self, user_name):
        """Adds a new user to the list of users.
        Args:
            user_name (str): The name of the new user.
        Returns:
            str: An error message if the user addition fails, or
            None if successful.
        """
        data = self._load_data()

        for user in data:
            if user['name'] == user_name:
                return "User with this name already exists."

        user_id = str(len(data) + 1)

        new_user = {
            'user_id': user_id,
            'name': user_name,
            'movies': []
        }

        data.append(new_user)
        self._write_data(data)

        return None, user_name

    def get_user_movies(self, user_id):
        """Returns the movies of a specific user.
        Args:
            user_id (str): The ID of the user.
        Returns:
            list: The movies of the user, or an empty list if the user
            doesn't exist.
        """
        data = self._load_data()
        for user in data:
            if user['user_id'] == user_id:
                return user['movies']
        return []

    def add_movie(self, user_id, movie_title):
        """Adds a movie to a user's list of movies.
        The movie details are fetched from the OMDb API.
        Args:
            user_id (str): The ID of the user.
            movie_title (str): The title of the movie.
        Returns:
            str: An error message if the movie wasn't found, or None
            if the movie was added successfully.
        """
        response = requests.get('http://www.omdbapi.com/',
                                params={'t': movie_title,
                                        'apikey': '5eeb20d'})
        movie_details = response.json()

        if movie_details['Response'] == 'True':
            movie_data = {
                'name': movie_details['Title'],
                'director': movie_details['Director'],
                'year': int(movie_details['Year']),
                'rating': float(movie_details['imdbRating'])
                if 'imdbRating' in movie_details and movie_details[
                                        'imdbRating'] != 'N/A' else 0.0
            }

            user_id = str(user_id)
            data = self._load_data()
            for user in data:
                if user['user_id'] == user_id:
                    max_id = max((movie['id'] for movie in user['movies']),
                                 default=0)

                    movie_data['id'] = max_id + 1
                    user['movies'].append(movie_data)
                    break
            self._write_data(data)
        else:
            return movie_details['Error']

        return None

    def get_movie(self, user_id, movie_id):
        """Returns a specific movie of a specific user.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.
        Returns:
            dict: The movie, or None if the movie doesn't exist.
        """
        user_id = str(user_id)
        movie_id = int(movie_id)
        data = self._load_data()
        for user in data:
            if user['user_id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        return movie
        return None

    def update_movie(self, user_id, movie_id, updated_movie):
        """Updates a specific movie of a specific user.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.
            updated_movie (dict): The updated movie details.
        """
        user_id = str(user_id)
        movie_id = int(movie_id)
        data = self._load_data()
        for user in data:
            if user['user_id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        movie.update(updated_movie)
                        self._write_data(
                            data)
                        return
        return

    def delete_movie(self, user_id, movie_id):
        """Deletes a specific movie of a specific user.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.
        """
        user_id = str(user_id)
        movie_id = int(movie_id)
        data = self._load_data()
        for user in data:
            if user['user_id'] == user_id:
                user['movies'] = [movie for movie in user['movies']
                                  if int(movie['id']) != movie_id]
                break
        self._write_data(data)
