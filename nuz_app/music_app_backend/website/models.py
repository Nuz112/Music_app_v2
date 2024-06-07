from website.database import db  
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    white_list = db.Column(db.Boolean, default = True)

    playlists = db.relationship('Playlist', backref= 'user', lazy = True)
    songs = db.relationship('Song', backref= 'user', lazy = True)   
    albums = db.relationship('Album', backref= 'user', lazy = True)
    activeTime = db.Column(db.Date, default=datetime.utcnow().date)

    def is_creator(self):
        return len(self.songs)
        

    def serialize(self):
        return {
            'id' : self.id,
            'email' :self.email,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'white_list' : self.white_list,
            'is_creator' : self.is_creator(),
            'activeTime': self.activeTime
        }





# Define the many-to-many relationship table between playlists and songs
playlist_song_association = db.Table(
    'playlist_song_association',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)



# Define the many-to-many relationship table between playlists and songs
album_song_association = db.Table(
    'album_song_association',
    db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    lyrics = db.Column(db.String(5000))
    singer = db.Column(db.String(150))
    genre = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(), default = func.now())
    ratings = db.Column(db.Float, default=0.0)
    num_ratings = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    albums = db.relationship('Album', secondary= album_song_association, back_populates='album_songs')
    playlists = db.relationship('Playlist', secondary= playlist_song_association, back_populates='songs')

    def serialize(self):
        return {
        'id': self.id,
        'name': self.name,
        'singer': self.singer,
        'lyrics': self.lyrics,
        'genre': self.genre,
        'ratings': self.ratings
        # Add any other attributes you want to include in the serialized representation
    }

    


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    rating = db.Column(db.Integer)

    


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(), default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    songs = db.relationship('Song', secondary=playlist_song_association, back_populates='playlists')

    def serialize(self):
        return {
        'id': self.id,
        'name': self.name,
        'user_id': self.user_id,
        'length': len(self.songs) if self.songs else 0,
    }



class Album(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    genre = db.Column(db.String(150))
    artist = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(), default = func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    album_songs = db.relationship('Song', secondary=album_song_association, back_populates='albums') 


    def serialize(self):
        return {
        'id': self.id,
        'name': self.name,
        'user_id': self.user_id,
        'length': len(self.album_songs) if self.album_songs else 0,
    }




