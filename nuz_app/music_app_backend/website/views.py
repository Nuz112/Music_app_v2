from flask import  Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from  website.database import db
from .models import Song, Rating,  User
from sqlalchemy import or_



views = Blueprint('views', __name__)





@views.route('/get_songs')
def get_songs():
    songs = Song.query.all()
    return jsonify([song.serialize() for song in songs])


@views.route('/filter_songs', methods=['POST'])
def filter_songs():
    data =  request.get_json(force=True)
    selected_genre = data.get('selectedGenre', 'All')


    if selected_genre == 'All':
        songs = Song.query.all()
    else:
        songs = Song.query.filter_by(genre=selected_genre).all()

    return jsonify({'messages' :"Done", 'songs': [song.serialize() for song in songs]})





@views.route('/upload_song', methods=['POST'])
@jwt_required()
def upload_song():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'Please login first'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.white_list:
        return jsonify({'message': "You are in a Black Listed by Admin, You couldn't upload a Song"})

    data = request.get_json(force=True)
    if not data:
        return jsonify({'message': 'No data received'}), 400

    song_name = data.get('songName')
    singer_name = data.get('singerName')
    lyrics = data.get('lyrics')
    genre = data.get('genre')
 

    if not song_name or not singer_name or not lyrics  or not genre:
        return jsonify({ 'message': 'Missing required fields'}), 400

    # Create a new song instance and populate its attributes
    new_song = Song(
        name=song_name,
        singer=singer_name,
        lyrics=lyrics,
        genre=genre,
        user_id=user_id
    )

    # Add the song to the database
    db.session.add(new_song)
    db.session.commit()
   
    return jsonify({'message': 'Song Upload Succesfully', 'success': True})










@views.route('/rate_song/<int:song_id>', methods=['POST'])
@jwt_required()
def rate_song(song_id):
    # Extract the rating value from the request data
    rating = request.json.get('rating')

    user_id = get_jwt_identity()
    prev_rating = Rating.query.filter_by(song_id=song_id, user_id=user_id).first()
    prev_rate = prev_rating.rating if prev_rating else None

    print(prev_rate)
    if not prev_rate:
    # Validate the rating value
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Invalid rating value. Rating must be an integer between 1 and 5.'}), 400

        # Find the song in the database
        song = Song.query.get(song_id)
        if not song:
            return jsonify({'error': 'Song not found.'}), 404

        # Update the song's rating
        song.ratings = ((song.ratings * song.num_ratings) + rating) / (song.num_ratings + 1)
        song.num_ratings += 1
        new_rating = Rating(user_id=user_id, song_id=song_id, rating = rating)

        # Save the changes to the database
        db.session.add(new_rating)
        db.session.commit()

        return jsonify({'success': True,'message': 'Song rated successfully.'}), 200
    return jsonify({'message' : "You've already rated this song"})





@views.route('/uploaded_songs', methods=['GET'])
@jwt_required()
def get_uploaded_songs():
    user_id = get_jwt_identity()
    # Query the database to get all uploaded songs
    uploaded_songs = Song.query.filter_by(user_id=user_id).all()

    # Serialize the songs data
    serialized_songs = [song.serialize() for song in uploaded_songs]

    return jsonify(serialized_songs)








@views.route('/delete_song/<int:song_id>', methods=['POST'])
def delete_song(song_id):

    try:
        song_to_delete = Song.query.filter_by(id=song_id).first()

        if song_to_delete:
            # Mark the song for deletion
            print(f"Deleting song: {song_to_delete.name}")
            db.session.delete(song_to_delete)
            db.session.commit()
            print('Song Deleted Succesfully')
            return jsonify({'message': 'Song deleted successfully'}), 200
        else:
            return jsonify({'error': 'Song not found or you do not have permission to delete it'}), 404
    except Exception as e:
        return jsonify({'error': f'Error deleting song: {str(e)}'}), 500




@views.route('/edit_song/<int:song_id>', methods=['PUT'])
def edit_song(song_id):
    try:
        # Get the song from the database
        song = Song.query.get(song_id)
        if song:
            print("Before Updatation Song Lyrics", request.json.get('lyrics', song.lyrics))
            # Update song information based on request data
            song.name = request.json.get('songName', song.name)
            song.singer = request.json.get('singerName', song.singer)
            song.genre = request.json.get('genre', song.genre)
            song.lyrics = request.json.get('lyrics', song.lyrics)
            db.session.commit()

            print("After Updatation Song Lyrics", request.json.get('lyrics', song.lyrics))

            return jsonify({'message': 'Song updated successfully'}), 200
        else:
            return jsonify({'error': 'Song not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error updating song: {str(e)}'}), 500



@views.route('/user_summary', methods=['GET'])
@jwt_required()
def user_summary():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Number of songs uploaded by the user
    num_songs = len(user.songs)

    # Number of playlists created by the user 
    num_playlists = len(user.playlists)

    # Number of albums created by the user
    num_albums = len(user.albums)

    # Average rating of all songs uploaded by the user
    total_rating = 0
    for song in user.songs:
        total_rating += song.ratings
    average_rating = total_rating / num_songs if num_songs > 0 else 0

    # The song(s) with the highest rating uploaded by the user
    highest_rated_songs = (
        Song.query.filter_by(user_id=user_id)
        .order_by(Song.ratings.desc())
        .limit(5)  # You can limit to a specific number of top-rated songs
        .all()
    )

    return jsonify({'user' : user.serialize(), 'num_songs': num_songs, 'num_playlists': num_playlists, 'num_albums': num_albums, 'average_rating': average_rating, 'highest_rated_songs':[song.serialize() for song in highest_rated_songs], 'success': True})






@views.route('/search_songs', methods=['POST'])
def search_songs():
    data = request.get_json()
    query = data.get('searchQuery')

    search_results = db.session.query(Song).filter(
        or_(Song.name.ilike(f'%{query}%'), Song.singer.ilike(f'%{query}%'))
        ).all()
    songs = [song.serialize() for song in search_results]
    

    if songs:
        return jsonify({ 'songs': songs, 'success' : True })
    
    else:
        return jsonify({'message': 'No result Found'})

