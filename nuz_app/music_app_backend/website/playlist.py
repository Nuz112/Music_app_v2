from flask import Blueprint, render_template, url_for, session, redirect, render_template, flash, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from website.database import db
from .models import Song, Playlist, playlist_song_association
from .auth import cache



playlist = Blueprint('playlist', __name__)



@playlist.route('/get_playlists', methods=[ 'GET'])
@cache.cached(timeout=5)
@jwt_required()
def get_playlists():
    user_id = get_jwt_identity()
    playlists = Playlist.query.filter_by(user_id = user_id).all()
    return jsonify([playlist.serialize() for playlist in playlists])





@playlist.route('/add_to_playlist/<int:song_id>', methods=[ 'POST'])
@jwt_required()
def add_to_playlist_api(song_id):
    data = request.json
    current_user_id = get_jwt_identity()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    playlist_id = data.get('playlist_id')
    new_playlist_name = data.get('new_playlist')

    if not playlist_id and not new_playlist_name:
        return jsonify({'error': 'Please provide a playlist ID or a new playlist name'}), 400

    song = Song.query.get(song_id)

    if not song:
        return jsonify({'error': 'Song not found'}), 404

    if playlist_id:
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Selected playlist not found'}), 404
        playlist.songs.append(song)
        db.session.commit()
        return jsonify({'message': 'Song added to the selected playlist'}), 200

    if new_playlist_name:
        new_playlist = Playlist(name=new_playlist_name, user_id=current_user_id)
        new_playlist.songs.append(song)
        db.session.add(new_playlist)
        db.session.commit()
        return jsonify({'message': 'Song added to the new playlist'}), 200

    return jsonify({'error': 'Unexpected error occurred'}), 500







@playlist.route('/select_playlist')
def select_playlist():
    user_id = session.get('user')
    user_name = session.get('user_name')

    # Retrieve the user's playlists
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    return render_template('select_playlist.html', playlists=playlists, user_name=user_name)






@playlist.route('/user_selected_playlist/<int:playlist_id>')
@jwt_required()
def user_selected_playlist(playlist_id):
    user_id = get_jwt_identity()
    
    # Retrieve the selected playlist
    playlist = Playlist.query.filter_by(user_id=user_id, id=playlist_id).first()
    
    if playlist:
        songs = [song.serialize() for song in playlist.songs]
        return jsonify({'success': True, 'songs': songs, 'playlist':playlist.serialize(), 'message': 'Render Songs from playlist successfully'})
    else:
        return jsonify({'error': 'There is no playlist for this user'})




@playlist.route('/remove_from_playlist/<int:playlist_id>/<int:song_id>', methods=['DELETE'])
@jwt_required()
def remove_from_playlist(playlist_id, song_id):
    user_id = get_jwt_identity()

    # Check if the user owns the playlist and the song
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
    songs= playlist.songs
    song = Song.query.filter_by(id=song_id).first()
    print(songs)
    if request.method == 'DELETE' :
        if playlist and song:
            if (song in playlist.songs):
                playlist.songs.remove(song)
                db.session.commit()
                return jsonify({'message': 'Song removed from the playlist',  'success': True})
            else:
                return jsonify({'error': 'Song is not in the selected playlist'})
        else:
            return jsonify({ 'error': 'Song or playlist not found, or you do not have permission to remove the song from the playlist'})






@playlist.route('/delete_playlist/<int:playlist_id>', methods= ['DELETE'])
@jwt_required()
def delete_playlist(playlist_id):
    # Get the user ID from the session
    user_id = get_jwt_identity()

    # Retrieve the selected playlist
    playlist = Playlist.query.filter_by(user_id=user_id, id=playlist_id).first()

    if playlist:
        try:
            # Remove the songs from the playlist
            playlist.songs.clear()
            
            # Delete the playlist
            db.session.delete(playlist)
            db.session.commit()
        
            return jsonify({'message': 'Playlist Delete Successfully'})
        except Exception as e:
            # Handle any potential errors
            db.session.rollback()
            return jsonify({ 'error': f'Error deleting playlist: {str(e)}'})
    else:
        return jsonify({'error': 'Selected Playlist is not found'})

    




@playlist.route('/search_playlist', methods=['POST'])
@jwt_required()
def search_playlist():
    data = request.get_json()
    query = data.get('searchQuery')
    user_id = get_jwt_identity()

    # Assuming that Playlist has a relationship with User
    user_playlists = db.session.query(Playlist).filter(
        Playlist.name.ilike(f'%{query}%'),
        Playlist.user_id == user_id
    ).all()
    
    if user_playlists:
        return jsonify({'success': True, 'playlists': [playlist.serialize() for playlist in user_playlists]})
    
    else:
        return jsonify({'message': 'No result Found'})


