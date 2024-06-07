from flask import Blueprint, render_template, url_for, session, redirect, render_template, flash, request, jsonify
from  website.database import db
from .models import Song, Album
from flask_jwt_extended import get_jwt_identity, jwt_required


album = Blueprint('album', __name__)


@album.route('/view_albums', methods= [ 'GET'])
@jwt_required()
def view_albums():
    user_id = get_jwt_identity()
    albums = Album.query.filter_by().all()

    return jsonify({'albums':[album.serialize() for album in albums], 'current_user' : user_id})







@album.route('/create_album', methods=['POST'])
@jwt_required()
def create_album():
    user_id = get_jwt_identity()
    album_name = request.json.get('album_name')
    selected_song_ids = request.json.get('selected_songs', [])
    
    album = Album(name=album_name, user_id=user_id)
    db.session.add(album)
    
    # Add selected songs to the album
    selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
    album.album_songs.extend(selected_songs)

    db.session.commit()
    return jsonify({'message': 'Album created successfully'}), 201


@album.route('/get_user_songs', methods=['GET'])
@jwt_required()
def get_user_songs():
    user_id = get_jwt_identity()
    songs = Song.query.filter_by(user_id = user_id)
    if songs:
        return jsonify({'songs': [song.serialize() for song in songs], "success" : True})
    
    return jsonify({'error': 'First you have to upload songs for create an album'})








@album.route('/user_selected_album/<int:album_id>', methods=['GET'])
@jwt_required()
def user_selected_album(album_id):
    user_id = get_jwt_identity()
    album = Album.query.filter_by(id=album_id).first()
    if album:
        songs = [song.serialize() for song in album.album_songs]
        return jsonify({'success': True, 'songs': songs, 'album':album.serialize(), 'message': 'Render Songs from album successfully', "current_user": user_id})
    else:
        return jsonify({'error': 'There is no album  with this album id'})








@album.route('/remove_from_album/<int:album_id>/<int:song_id>', methods=['DELETE'])
@jwt_required()
def remove_from_playlist(album_id, song_id):
    user_id = get_jwt_identity()

    # Check if the user owns the playlist and the song
    album = Album.query.filter_by(id=album_id, user_id=user_id).first()
    songs= album.album_songs
    song = Song.query.filter_by(id=song_id).first()
    if request.method == 'DELETE' :
        if album and song:
            if (song in album.album_songs):
                album.album_songs.remove(song)
                db.session.commit()
                return jsonify({'message': 'Song removed from the album',  'success': True})
            else:
                return jsonify({'error': 'Song is not in the selected album'})
        else:
            return jsonify({ 'error': 'Song or album not found, or you do not have permission to remove the song from the album'})






@album.route('/delete_album/<int:album_id>', methods= ['DELETE'])
@jwt_required()
def delete_playlist(album_id):
    # Get the user ID from the session
    user_id = get_jwt_identity()

    # Retrieve the selected playlist
    album = Album.query.filter_by(user_id=user_id, id=album_id).first()

    if album:
        try:
            album.album_songs.clear()
            
            # Delete the playlist
            db.session.delete(album)
            db.session.commit()
        
            return jsonify({'message': 'Album Delete Successfully'})
        except Exception as e:
            # Handle any potential errors
            db.session.rollback()
            return jsonify({ 'error': f'Error deleting album: {str(e)}'})
    else:
        return jsonify({'error': 'Selected album is not found'})


@album.route('/search_album', methods=['POST'])
def search_album():
    data = request.get_json()
    query = data.get('searchQuery')
    search_results = db.session.query(Album).filter(Album.name.ilike(f'%{query}%')).all()
    if search_results:
        
        return jsonify({'success': True, 'albums': [album.serialize() for album in search_results]})

    else:
        return jsonify({'message': 'No result Found'})







@album.route('/add_songs_to_album/<int:album_id>', methods=['POST'])
@jwt_required()
def add_songs_to_album(album_id):
    user_id = get_jwt_identity()
    album = Album.query.filter_by(id = album_id, user_id= user_id).first()
    selected_song_ids = request.json.get('selected_songs', [])
    selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
    album.album_songs.extend(selected_songs)
    db.session.commit()
    songs = album.album_songs
    return jsonify({'songs' : [song.serialize() for song in songs], 'album': album.serialize()} ) 



@album.route('get_remaining_songs/<int:album_id>', methods=['GET'])
@jwt_required()
def get_remaining_songs(album_id):
    user_id = get_jwt_identity()
    album = Album.query.filter_by(id = album_id, user_id= user_id).first()
    print(album)
    # Query to get songs that are not in the album
    remaining_songs = Song.query.filter(~Song.albums.any(id=album.id)).filter_by(user_id = user_id).all()
    
    return jsonify({'remaining_songs' : [song.serialize() for song in remaining_songs], 'album': album.serialize(), 'success': True} )
