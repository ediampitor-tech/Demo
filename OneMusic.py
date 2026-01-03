# app.py - Main application file
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import json
import requests
from datetime import datetime, timedelta
import hashlib
import stripe
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_streaming.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Stripe configuration
stripe_keys = {
    'secret_key': os.getenv('STRIPE_SECRET_KEY', 'your-stripe-secret-key'),
    'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY', 'your-stripe-publishable-key')
}
stripe.api_key = stripe_keys['secret_key']

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscription_type = db.Column(db.String(20), default='free')
    subscription_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    genre = db.Column(db.String(100))
    duration = db.Column(db.Integer)  # in seconds
    audio_url = db.Column(db.String(500))
    cover_art = db.Column(db.String(500))
    plays = db.Column(db.Integer, default=0)
    
    favorites = db.relationship('Favorite', backref='song', lazy=True)
    playlist_songs = db.relationship('PlaylistSong', backref='song', lazy=True)

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

# Music API Integration
class MusicAPI:
    def __init__(self):
        self.base_url = "https://api.deezer.com"
        self.cache = {}
    
    def search_songs(self, query, limit=50):
        """Search for songs using Deezer API (free tier available)"""
        cache_key = f"search_{query}_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = requests.get(f"{self.base_url}/search", params={'q': query, 'limit': limit})
            if response.status_code == 200:
                data = response.json()
                songs = []
                for track in data.get('data', []):
                    song = {
                        'id': track['id'],
                        'title': track['title'],
                        'artist': track['artist']['name'],
                        'album': track['album']['title'],
                        'duration': track['duration'],
                        'preview': track['preview'],
                        'cover_art': track['album']['cover_medium'],
                        'link': track['link']
                    }
                    songs.append(song)
                self.cache[cache_key] = songs
                return songs
        except Exception as e:
            print(f"API Error: {e}")
            return []
    
    def get_chart(self):
        """Get top charts"""
        try:
            response = requests.get(f"{self.base_url}/chart")
            if response.status_code == 200:
                return response.json()
        except:
            return None
    
    def get_artist_top_tracks(self, artist_id, limit=10):
        """Get artist's top tracks"""
        try:
            response = requests.get(f"{self.base_url}/artist/{artist_id}/top", params={'limit': limit})
            if response.status_code == 200:
                return response.json()
        except:
            return None

music_api = MusicAPI()

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'standard': {
        'name': 'Standard',
        'price': 1.5,
        'features': ['Ad-free listening', 'Download songs', 'High quality audio'],
        'stripe_price_id': 'price_standard'  # You'll create this in Stripe Dashboard
    },
    'dual': {
        'name': 'Dual',
        'price': 3.0,
        'features': ['Everything in Standard', '2 simultaneous devices', 'Shared playlists'],
        'stripe_price_id': 'price_dual'
    },
    'family': {
        'name': 'Family',
        'price': 8.0,
        'features': ['Everything in Dual', 'Up to 6 accounts', 'Family mix playlists'],
        'stripe_price_id': 'price_family'
    }
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', plans=SUBSCRIPTION_PLANS)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recommended songs
    chart_data = music_api.get_chart()
    top_tracks = chart_data.get('tracks', {}).get('data', [])[:20] if chart_data else []
    
    # Get user's playlists
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         top_tracks=top_tracks,
                         playlists=playlists,
                         plans=SUBSCRIPTION_PLANS)

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        results = music_api.search_songs(query)
    return render_template('search.html', results=results, query=query)

@app.route('/play/<int:song_id>')
@login_required
def play_song(song_id):
    # In a real app, you'd fetch from your database
    # For demo, we'll use API
    song = None
    try:
        response = requests.get(f"{music_api.base_url}/track/{song_id}")
        if response.status_code == 200:
            song = response.json()
    except:
        pass
    
    if song:
        # Log play count
        db_song = Song.query.filter_by(id=song_id).first()
        if db_song:
            db_song.plays += 1
            db.session.commit()
    
    return render_template('player.html', song=song)

@app.route('/playlist/create', methods=['POST'])
@login_required
def create_playlist():
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    if name:
        playlist = Playlist(name=name, description=description, user_id=current_user.id)
        db.session.add(playlist)
        db.session.commit()
        return jsonify({'success': True, 'id': playlist.id})
    
    return jsonify({'success': False})

@app.route('/playlist/<int:playlist_id>')
@login_required
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    return render_template('playlist.html', playlist=playlist)

@app.route('/favorite/<int:song_id>', methods=['POST'])
@login_required
def toggle_favorite(song_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, song_id=song_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'favorited': False})
    else:
        favorite = Favorite(user_id=current_user.id, song_id=song_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'favorited': True})

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        hashed_password = hash_password(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Premium Subscription Routes
@app.route('/premium')
@login_required
def premium():
    return render_template('premium.html', plans=SUBSCRIPTION_PLANS, 
                         stripe_publishable_key=stripe_keys['publishable_key'])

@app.route('/create-checkout-session/<plan_type>', methods=['POST'])
@login_required
def create_checkout_session(plan_type):
    if plan_type not in SUBSCRIPTION_PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': SUBSCRIPTION_PLANS[plan_type]['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('premium', _external=True),
            customer_email=current_user.email,
            metadata={
                'user_id': current_user.id,
                'plan_type': plan_type
            }
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/payment-success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')
    
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Update user subscription
        if checkout_session.payment_status == 'paid':
            plan_type = checkout_session.metadata.get('plan_type')
            current_user.subscription_type = plan_type
            current_user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
            db.session.commit()
            
            return render_template('payment_success.html', plan=SUBSCRIPTION_PLANS.get(plan_type, {}))
    except Exception as e:
        print(f"Payment success error: {e}")
    
    return redirect(url_for('premium'))

# Admin Routes
@app.route('/admin/add-song', methods=['POST'])
@login_required
def add_song():
    if current_user.subscription_type != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    song = Song(
        title=data['title'],
        artist=data['artist'],
        album=data.get('album', ''),
        genre=data.get('genre', ''),
        duration=data['duration'],
        audio_url=data['audio_url'],
        cover_art=data.get('cover_art', '')
    )
    db.session.add(song)
    db.session.commit()
    
    return jsonify({'success': True, 'id': song.id})

# Utility functions
def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hash_password(user_password)

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add some sample songs
        if Song.query.count() == 0:
            sample_songs = [
                Song(title="Blinding Lights", artist="The Weeknd", album="After Hours", 
                     genre="Pop", duration=200, audio_url="/static/audio/sample1.mp3",
                     cover_art="https://e-cdns-images.dzcdn.net/images/cover/5b1a3f..."),
                Song(title="Stay", artist="The Kid LAROI, Justin Bieber", album="F*CK LOVE 3",
                     genre="Pop", duration=141, audio_url="/static/audio/sample2.mp3",
                     cover_art="https://e-cdns-images.dzcdn.net/images/cover/2e0181..."),
                Song(title="Good 4 U", artist="Olivia Rodrigo", album="SOUR",
                     genre="Pop Rock", duration=178, audio_url="/static/audio/sample3.mp3",
                     cover_art="https://e-cdns-images.dzcdn.net/images/cover/cc3f80..."),
            ]
            for song in sample_songs:
                db.session.add(song)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)