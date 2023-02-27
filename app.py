# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# Создаем апи
api = Api(app)
# Регистрируем namespaces
movie_ns = api.namespace("/movies")
director_ns = api.namespace("/directors")
genre_ns = api.namespace("/genres")

with app.app_context():
    db.create_all()


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        """ Получение всех фильмов """
        try:
            d = request.args.get("director_id", type=int)
            g = request.args.get("genre_id", type=int)
            if d and g:
                movies = db.session.query(Movie).filter(Movie.director_id == d, Movie.genre_id == g).all()
                if movies != []:
                    return movies_schema.dump(movies), 200
                else:
                    return "Не найдено полных сопадений!"
            elif d or g:
                movies = db.session.query(Movie).filter(or_(Movie.director_id == d, Movie.genre_id == g)).all()
                if movies != []:
                    return movies_schema.dump(movies), 200
                else:
                    return "Не найдено каких-либо параметров! Скорректируйте значения!"
            else:
                all_movies = Movie.query.all()
                return movies_schema.dump(all_movies), 200

        except Exception as e:
            return str(e), 404

    def post(self):
        """ Добавление нового фильма """
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Фильм добавлен"


@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        """ Получение фильмa по mid"""
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid):
        """ Обновление фильма по mid"""
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            req_json = request.json

            movie.title = req_json.get("title")
            movie.description = req_json.get("description")
            movie.trailer = req_json.get("trailer")
            movie.year = req_json.get("year")
            movie.rating = req_json.get("rating")
            movie.genre_id = req_json.get("genre_id")
            movie.director_id = req_json.get("director_id")

            db.session.add(movie)
            db.session.commit()

            return "Данные о фильме обновлены", 201
        except Exception as e:
            return str(e), 404

    def delete(self, mid):
        """ Удаление фильма по mid"""
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()

            db.session.delete(movie)
            db.session.commit()

            return "Данные о фильме удалены", 201
        except Exception as e:
            return str(e), 404


@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        """ Получение всех режиссеров """
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        """ Добавление нового режиссера """
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Режиссер добавлен"


@director_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        """ Получение режиссера по did"""
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, did):
        """ Обновление режиссера по did"""
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            req_json = request.json

            director.name = req_json.get("name")

            db.session.add(director)
            db.session.commit()

            return "Данные о режиссере обновлены", 201
        except Exception as e:
            return str(e), 404

    def delete(self, did):
        """ Удаление режиссера по did"""
        try:
            director = db.session.query(Director).filter(Director.id == did).one()

            db.session.delete(director)
            db.session.commit()

            return "Данные о режиссере удалены", 201
        except Exception as e:
            return str(e), 404


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        """ Получение всех жанров """
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        """ Добавление нового жанра """
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "Жанр добавлен"


@genre_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid):
        """ Получение жанра по gid"""
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, gid):
        """ Обновление жанра по gid"""
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()
            req_json = request.json

            genre.name = req_json.get("name")

            db.session.add(genre)
            db.session.commit()

            return "Данные о жанре обновлены", 201
        except Exception as e:
            return str(e), 404

    def delete(self, gid):
        """ Удаление жанра по gid"""
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()

            db.session.delete(genre)
            db.session.commit()

            return "Данные о жанре удалены", 201
        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
