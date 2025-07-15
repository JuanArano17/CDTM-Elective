from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # For simplicity, no password/auth for now
    words = db.relationship('Word', backref='user', lazy=True)
    topics = db.relationship('Topic', backref='user', lazy=True)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Null for default topics
    words = db.relationship('Word', backref='topic', lazy=True)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(80), nullable=False)
    spanish = db.Column(db.String(80), nullable=True)
    french = db.Column(db.String(80), nullable=True)
    italian = db.Column(db.String(80), nullable=True)
    pronunciation = db.Column(db.String(120), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    notes = db.relationship('Note', backref='word', lazy=True)
    images = db.relationship('Image', backref='word', lazy=True)
    flashcard_stats = db.relationship('FlashcardStat', backref='word', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)

class FlashcardStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    times_reviewed = db.Column(db.Integer, default=0)
    last_result = db.Column(db.String(10), nullable=True)  # 'Easy', 'Medium', 'Hard'
    familiarity = db.Column(db.Float, default=0.0)  # For spaced repetition 