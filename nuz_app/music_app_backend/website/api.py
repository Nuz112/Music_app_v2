from flask import Blueprint, request, jsonify ,current_app as app
from flask_restful import Api, Resource
from .models import db, Song, Playlist, Album
from website import tasks
from flask_caching import Cache
from datetime import datetime
cash = Cache(app)


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class SongResource(Resource):
    def get(self, song_id=None):
        if song_id:
        # If song_id is provided, fetch a single song
            song = Song.query.get_or_404(song_id)
            song_info = {
                'id': song.id,
                'name': song.name,
                'lyrics': song.lyrics,
                'singer': song.singer,
                'genre': song.genre,
                'created_at': song.created_at.isoformat(),
                'ratings': song.ratings,
                'num_ratings': song.num_ratings,
                'user_id': song.user_id
            }
            return jsonify(song_info)
        else:
            # If no song_id is provided, fetch all songs
            songs = Song.query.all()
            song_list = []
            for song in songs:
                song_info = {
                    'id': song.id,
                    'name': song.name,
                    'lyrics': song.lyrics,
                    'singer': song.singer,
                    'genre': song.genre,
                    'created_at': song.created_at.isoformat(),
                    'ratings': song.ratings,
                    'num_ratings': song.num_ratings,
                    'user_id': song.user_id
                }
                song_list.append(song_info)

            return jsonify({'songs': song_list})

    def put(self, song_id):
        song = Song.query.get_or_404(song_id)
        # Update the song attributes based on the request data
        data = request.get_json()
        song.name = data.get('name', song.name)
        song.lyrics = data.get('lyrics', song.lyrics)
        song.singer =data.get('singer', song.singer)
        song.genre = data.get('genre', song.genre)

        db.session.commit()
        return {'message': 'Song updated successfully'}

    def delete(self, song_id):
        song = Song.query.get_or_404(song_id)
        db.session.delete(song)
        db.session.commit()
        return {'message': 'Song deleted successfully'}
    





class PlaylistResource(Resource):
    
    @cash.cached(timeout=5)
    def get(self, playlist_id=None):
        if playlist_id:
            # If playlist_id is provided, fetch a single playlist
            playlist = Playlist.query.get_or_404(playlist_id)
            playlist_info = {
                'id': playlist.id,
                'name': playlist.name,
                'created_at': playlist.created_at.isoformat(),
                'user_id': playlist.user_id,
                'songs': [song.serialize() for song in playlist.songs]
            }
            return jsonify(playlist_info)
        else:
            # If no playlist_id is provided, fetch all playlists
            playlists = Playlist.query.all()
            playlist_list = []
            for playlist in playlists:
                playlist_info = {
                    'id': playlist.id,
                    'name': playlist.name,
                    'created_at': playlist.created_at.isoformat(),
                    'user_id': playlist.user_id,
                    'songs_count': len(playlist.songs)
                }
                playlist_list.append(playlist_info)
            return jsonify({'playlists': playlist_list})

    def post(self):
        data = request.get_json()
        name = data.get('name')
        user_id = data.get('user_id')

        if not name:
            return jsonify({'message': 'Name is required for creating a playlist.'}), 400

        new_playlist = Playlist(name=name, user_id=user_id)
        db.session.add(new_playlist)
        db.session.commit()

        return jsonify({'message': 'Playlist created successfully', 'playlist_id': new_playlist.id}), 201

    def put(self, playlist_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        data = request.get_json()
        name = data.get('name')

        if not name:
            return jsonify({'message': 'Name is required for updating a playlist.'}), 400

        playlist.name = name
        db.session.commit()

        return jsonify({'message': 'Playlist updated successfully'})

    def delete(self, playlist_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        db.session.delete(playlist)
        db.session.commit()
        return jsonify({'message': 'Playlist deleted successfully'})






class AlbumResource(Resource):
    def get(self, album_id=None ):
        if album_id:
            # If album_id is provided, fetch a single album
            album = Album.query.get_or_404(album_id)
            return jsonify(album.serialize())
        else:
            # If no album_id is provided, fetch all albums
            albums = Album.query.all()
            album_list = [album.serialize() for album in albums]
            return jsonify({'albums': album_list})

    def post(self):
        data = request.get_json()
        new_album = Album(
            name=data.get('name'),
            genre=data.get('genre'),
            artist=data.get('artist'),
            user_id=data.get('user_id')
            # Add other attributes as needed
        )
        db.session.add(new_album)
        db.session.commit()
        return jsonify({'message': 'Album created successfully', 'album_id': new_album.id}), 201

    def put(self, album_id):

            album = Album.query.get_or_404(album_id)
        # if album.user_id == user_id:
            data = request.get_json()
            album.name = data.get('name', album.name)
            album.genre = data.get('genre', album.genre)
            album.artist = data.get('artist', album.artist)
            # Update other attributes similarly
            db.session.commit()
            return jsonify({'message': 'Album updated successfully'})
        # else:
        #     return jsonify({'message': "You're not authorized user"})

    def delete(self, album_id):
            album = Album.query.get_or_404(album_id)
        # if album.user_id == user_id:
            db.session.delete(album)
            db.session.commit()
            return jsonify({'message': 'Album deleted successfully'})
        # else:
        #     return jsonify({'message': "You're not authorized user"})



@app.route("/hello", methods=["GET","POST"])
def hello():
    now=datetime.now()
    print("now_in_flask = ", now)
    dt_string= now.strftime("%d/%m/%y %H:%M:%S")
    print("date and time ", dt_string)
    job = tasks.print_current_time.apply_async(countdown=10)
    result=job.wait()
    return str(result), 200




api.add_resource(SongResource,  '/song/',   '/song/<int:song_id>')
api.add_resource(PlaylistResource, '/playlist/', '/playlist/<int:playlist_id>')
api.add_resource(AlbumResource, '/albums/', '/albums/<int:album_id>')


