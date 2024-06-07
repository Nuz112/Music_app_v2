from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .models import User, Album, Playlist, Song,  db, playlist_song_association
from sqlalchemy.sql import func
from sqlalchemy import or_
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity




admin = Blueprint('admin', __name__)




@admin.route('/admin/login', methods=['POST'])
def admin_login():

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if this is the admin's email and password
    admin_email = "patelnujhat114@gmail.com"  
    admin_password = "nuj123"  

    if email == admin_email and password == admin_password:

        access_token = create_access_token(identity='admin_loggedin')
        
        session['admin'] = True

        return  jsonify({ 'success': True, 'messages': 'Admin Logged In Successfully', 'access_token': access_token})
    else:
        return jsonify({'messages': 'Admin login failed. Please check your credentials.'})

 







@admin.route('/admin/dashboard')
def admin_dashboard():

        num_users = User.query.count()
        num_albums = Album.query.count()
        top_rated_songs = Song.query.order_by(Song.ratings.desc()).limit(10).all()
        num_users_uploaded_songs = User.query.filter(User.songs.any()).count()
        songs = [song.serialize() for song in top_rated_songs]

        # Query for the top 5 most popular songs based on how many playlists include them
        top_popular_songs = db.session.query(
            Song, func.count(playlist_song_association.c.playlist_id)
        ).join(
            playlist_song_association
        ).group_by(
            Song
        ).order_by(
            func.count(playlist_song_association.c.playlist_id).desc()
        ).limit(5).all()

        labels = [song.name for song, _ in top_popular_songs]
        counts = [count for _, count in top_popular_songs]

        fig, ax = plt.subplots()
        ax.bar(labels, counts)
        ax.set_ylabel('Number of Playlists')
        ax.set_title('Top Songs by Playlist Count')

        ax.set_xticklabels(labels, rotation=35, ha='right')
        plt.subplots_adjust(bottom=0.3)

        # Save the plot to a BytesIO object
        img_io = BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)

        # Embed the plot in the HTML template
        img_data = base64.b64encode(img_io.read()).decode('utf-8')   
        # img_data = base64.b64encode(img_io.read())


        return jsonify({'success': True, 'num_albums': num_albums, 'num_users': num_users, 'num_users_uploaded_songs': num_users_uploaded_songs, 'top_rated_songs': songs, 'img_data': img_data})





        # return render_template('admin_dashboard.html',
        #                     num_users=num_users,
        #                     top_rated_songs=top_rated_songs,
        #                     num_users_uploaded_songs=num_users_uploaded_songs,
        #                     top_popular_songs =top_popular_songs,
        #                     num_albums = num_albums,
        #                     img_data = img_data
        #                     )







@admin.route('/admin/songs', methods=['GET'])
def songs():

    songs = Song.query.all()
    return jsonify({'songs': [song.serialize() for song in songs]})








@admin.route('admin/delete_song/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):

    song_to_delete = Song.query.filter_by(id=song_id).first()

    if song_to_delete:
        print(f"Deleting song: {song_to_delete.name}")
        db.session.delete(song_to_delete)
        db.session.commit()
        return jsonify({ 'success' : True})
    else :
        return jsonify({'message': 'File not found'})






@admin.route('/admin/album_songs/<album_id>')
def admin_album_songs(album_id):

    album = Album.query.filter_by(id = album_id).first()
    if album:
        songs = album.album_songs
        return jsonify({'success': True, 'songs': [song.serialize() for song in songs], 'album': album.serialize()})
    else:
        return jsonify({'message': 'Album not found'})






@admin.route('admin/albums')
def admin_albums():
        
        albums = Album.query.all()
        return jsonify({'albums': [album.serialize() for album in albums]})





@admin.route('admin/remove_from_album/<int:album_id>/<int:song_id>', methods=['POST'])
def remove_from_album(album_id, song_id):

    album= Album.query.filter_by(id=album_id).first()
    song = Song.query.filter_by(id=song_id).first()

    if album and song:
        if (song in album.album_songs):
            album.album_songs.remove(song)
            db.session.commit()
            return  jsonify({ 'success' : True})
        else:
            return jsonify({'message': 'Album or Song Not Found'})





@admin.route('admin/delete_album/<album_id>' , methods = ['DELETE'])
def delete_album( album_id ):

    album = Album.query.filter_by( id=album_id ).first()
    
    if album:
        for song in album.album_songs:
            album.album_songs.remove(song)

        db.session.delete(album)
        db.session.commit()
        
        return jsonify({'success': True})
    else:
        return jsonify({'message': 'Album not Found'})





@admin.route('/admin/user_list', methods=['GET'])
def user_list():
        
        users = User.query.all()

        return jsonify({'success': True, 'users': [user.serialize() for user in users]})
    



@admin.route('/admin/toggle_white_list/<int:user_id>', methods=['PUT'])
def toggle_white_list(user_id):
    user = User.query.get(user_id)
    if user:
        user.white_list = not user.white_list
        db.session.commit()
        return jsonify({'success': True})
    else :
        return jsonify({'message': 'User is Not Found'})


@admin.route('/admin/search_user', methods=['POST'])
def search_user():
    data = request.get_json()
    query = data.get('searchQuery')

    if query:
        users = db.session.query(User).filter(
                or_(
                User.email.ilike(f'%{query}%'),
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%')
                
            )
        ).all()

        return jsonify({'users': [user.serialize() for user in users], 'success': True})

    else:
        return jsonify({'message': 'File Not Found'})

