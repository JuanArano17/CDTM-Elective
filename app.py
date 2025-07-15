from flask import Flask, render_template, request, redirect, url_for, send_file, flash, abort, session
from flask_cors import CORS
import os
import pandas as pd
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
import io
import random

from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dictiown.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db.init_app(app)
CORS(app)

from models import Topic, Word, Note, Image, FlashcardStat

def init_db():
    from models import Topic, Word
    db.create_all()
    # Check if topics already exist
    if Topic.query.count() == 0:
        default_topics = [
            ("Animals", [
                ("cat", "gato", "chat", "gatto"),
                ("dog", "perro", "chien", "cane"),
                ("bird", "pájaro", "oiseau", "uccello"),
                ("fish", "pez", "poisson", "pesce"),
                ("horse", "caballo", "cheval", "cavallo"),
                ("cow", "vaca", "vache", "mucca"),
                ("sheep", "oveja", "mouton", "pecora"),
                ("pig", "cerdo", "cochon", "maiale"),
                ("mouse", "ratón", "souris", "topo"),
                ("lion", "león", "lion", "leone"),
            ]),
            ("Food", [
                ("bread", "pan", "pain", "pane"),
                ("cheese", "queso", "fromage", "formaggio"),
                ("apple", "manzana", "pomme", "mela"),
                ("milk", "leche", "lait", "latte"),
                ("egg", "huevo", "œuf", "uovo"),
                ("meat", "carne", "viande", "carne"),
                ("rice", "arroz", "riz", "riso"),
                ("chicken", "pollo", "poulet", "pollo"),
                ("fish", "pescado", "poisson", "pesce"),
                ("soup", "sopa", "soupe", "zuppa"),
            ]),
            ("Colors", [
                ("red", "rojo", "rouge", "rosso"),
                ("blue", "azul", "bleu", "blu"),
                ("green", "verde", "vert", "verde"),
                ("yellow", "amarillo", "jaune", "giallo"),
                ("black", "negro", "noir", "nero"),
                ("white", "blanco", "blanc", "bianco"),
                ("orange", "naranja", "orange", "arancione"),
                ("pink", "rosa", "rose", "rosa"),
                ("purple", "morado", "violet", "viola"),
                ("brown", "marrón", "marron", "marrone"),
            ]),
            ("Numbers", [
                ("one", "uno", "un", "uno"),
                ("two", "dos", "deux", "due"),
                ("three", "tres", "trois", "tre"),
                ("four", "cuatro", "quatre", "quattro"),
                ("five", "cinco", "cinq", "cinque"),
                ("six", "seis", "six", "sei"),
                ("seven", "siete", "sept", "sette"),
                ("eight", "ocho", "huit", "otto"),
                ("nine", "nueve", "neuf", "nove"),
                ("ten", "diez", "dix", "dieci"),
            ]),
            ("Emotions", [
                ("happy", "feliz", "heureux", "felice"),
                ("sad", "triste", "triste", "triste"),
                ("angry", "enojado", "fâché", "arrabbiato"),
                ("afraid", "asustado", "effrayé", "spaventato"),
                ("surprised", "sorprendido", "surpris", "sorpreso"),
                ("bored", "aburrido", "ennuyé", "annoiato"),
                ("tired", "cansado", "fatigué", "stanco"),
                ("excited", "emocionado", "excité", "eccitato"),
                ("nervous", "nervioso", "nerveux", "nervoso"),
                ("calm", "calmado", "calme", "calmo"),
            ]),
        ]
        for topic_name, words in default_topics:
            topic = Topic(name=topic_name)
            db.session.add(topic)
            db.session.flush()  # Get topic.id
            for eng, spa, fre, ita in words:
                word = Word(english=eng, spanish=spa, french=fre, italian=ita, topic_id=topic.id)
                db.session.add(word)
        db.session.commit()

@app.route('/')
def index():
    # Get topics and their words
    topics = Topic.query.filter_by(user_id=None).all()
    for topic in topics:
        topic.words = Word.query.filter_by(topic_id=topic.id).all()
    
    # Get words without topics
    unassigned_words = Word.query.filter_by(topic_id=None).all()
    
    return render_template('index.html', topics=topics, unassigned_words=unassigned_words)

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    topics = Topic.query.filter_by(user_id=None).all()
    if request.method == 'POST':
        english = request.form['english']
        spanish = request.form.get('spanish')
        french = request.form.get('french')
        italian = request.form.get('italian')
        pronunciation = request.form.get('pronunciation')
        topic_id = request.form.get('topic_id')
        note_content = request.form.get('note')
        
        # Convert empty topic_id to None
        topic_id = int(topic_id) if topic_id else None
        
        word = Word(
            english=english,
            spanish=spanish,
            french=french,
            italian=italian,
            pronunciation=pronunciation,
            topic_id=topic_id
        )
        
        db.session.add(word)
        db.session.flush()  # Get word.id
        
        if note_content:
            note = Note(content=note_content, word_id=word.id)
            db.session.add(note)
            
        db.session.commit()
        flash('Word added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_word.html', topics=topics)

@app.route('/topics')
def topics():
    topics = Topic.query.filter_by(user_id=None).all()
    for topic in topics:
        topic.words = Word.query.filter_by(topic_id=topic.id).all()
    return render_template('topics.html', topics=topics)

@app.route('/add_topic', methods=['GET', 'POST'])
def add_topic():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if name:
            topic = Topic(name=name, description=description)
            db.session.add(topic)
            db.session.commit()
            flash('Topic created successfully!')
            return redirect(url_for('topics'))
    return render_template('add_topic.html')

@app.route('/edit_topic/<int:topic_id>', methods=['GET', 'POST'])
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if name:
            topic.name = name
            topic.description = description
            db.session.commit()
            flash('Topic updated successfully!')
            return redirect(url_for('topics'))
    return render_template('add_topic.html', topic=topic)

@app.route('/delete_topic/<int:topic_id>')
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if topic.words:
        flash('Cannot delete topic with existing words. Please move or delete the words first.')
    else:
        db.session.delete(topic)
        db.session.commit()
        flash('Topic deleted successfully!')
    return redirect(url_for('topics'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Handle theme preference
        theme = request.form.get('theme', 'light')
        session['theme'] = theme
        
        # Handle study preferences
        session['cards_per_study'] = int(request.form.get('cards_per_study', 10))
        session['show_pronunciation'] = request.form.get('show_pronunciation') == 'on'
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))

    # Get statistics
    total_words = Word.query.count()
    total_topics = Topic.query.count()
    
    # Get flashcard statistics
    stats = FlashcardStat.query.all()
    total_reviews = sum(stat.times_reviewed or 0 for stat in stats)
    
    # Calculate difficulty distribution
    easy_count = FlashcardStat.query.filter_by(last_result='Easy').count()
    medium_count = FlashcardStat.query.filter_by(last_result='Medium').count()
    hard_count = FlashcardStat.query.filter_by(last_result='Hard').count()
    
    # Calculate mastery level (average familiarity)
    total_familiarity = sum(stat.familiarity or 0 for stat in stats)
    avg_familiarity = round((total_familiarity / len(stats)) * 100 if stats else 0, 1)
    
    # Get current preferences
    current_theme = session.get('theme', 'light')
    cards_per_study = session.get('cards_per_study', 10)
    show_pronunciation = session.get('show_pronunciation', True)

    return render_template('settings.html',
                         total_words=total_words,
                         total_topics=total_topics,
                         total_reviews=total_reviews,
                         easy_count=easy_count,
                         medium_count=medium_count,
                         hard_count=hard_count,
                         avg_familiarity=avg_familiarity,
                         current_theme=current_theme,
                         cards_per_study=cards_per_study,
                         show_pronunciation=show_pronunciation)

@app.route('/statistics')
def statistics():
    # Get overall statistics
    total_words = Word.query.count()
    total_topics = Topic.query.count()
    
    # Get flashcard statistics
    stats = FlashcardStat.query.all()
    total_reviews = sum(stat.times_reviewed or 0 for stat in stats)
    
    # Calculate overall mastery
    total_familiarity = sum(stat.familiarity or 0 for stat in stats)
    avg_familiarity = round((total_familiarity / len(stats)) * 100 if stats else 0, 1)
    
    # Calculate recall success rate
    easy_count = FlashcardStat.query.filter_by(last_result='Easy').count()
    medium_count = FlashcardStat.query.filter_by(last_result='Medium').count()
    hard_count = FlashcardStat.query.filter_by(last_result='Hard').count()
    total_rated = easy_count + medium_count + hard_count
    
    recall_rate = round(((easy_count + medium_count * 0.5) / total_rated * 100) if total_rated > 0 else 0, 1)
    
    # Get per-topic statistics
    topics = Topic.query.all()
    topic_stats = []
    for topic in topics:
        topic_words = Word.query.filter_by(topic_id=topic.id).all()
        topic_word_ids = [word.id for word in topic_words]
        topic_stats_records = FlashcardStat.query.filter(FlashcardStat.word_id.in_(topic_word_ids)).all()
        
        total_topic_reviews = sum(stat.times_reviewed or 0 for stat in topic_stats_records)
        topic_familiarity = sum(stat.familiarity or 0 for stat in topic_stats_records)
        avg_topic_familiarity = round((topic_familiarity / len(topic_stats_records)) * 100 if topic_stats_records else 0, 1)
        
        topic_easy = sum(1 for stat in topic_stats_records if stat.last_result == 'Easy')
        topic_medium = sum(1 for stat in topic_stats_records if stat.last_result == 'Medium')
        topic_hard = sum(1 for stat in topic_stats_records if stat.last_result == 'Hard')
        topic_total_rated = topic_easy + topic_medium + topic_hard
        
        topic_recall_rate = round(((topic_easy + topic_medium * 0.5) / topic_total_rated * 100) if topic_total_rated > 0 else 0, 1)
        
        topic_stats.append({
            'topic': topic,
            'word_count': len(topic_words),
            'total_reviews': total_topic_reviews,
            'mastery': avg_topic_familiarity,
            'recall_rate': topic_recall_rate
        })

    return render_template('statistics.html',
                         total_words=total_words,
                         total_topics=total_topics,
                         total_reviews=total_reviews,
                         avg_familiarity=avg_familiarity,
                         recall_rate=recall_rate,
                         topic_stats=topic_stats)

@app.route('/export_csv', methods=['POST'])
def export_csv():
    words = Word.query.all()
    data = [{
        'english': w.english,
        'spanish': w.spanish,
        'french': w.french,
        'italian': w.italian,
        'pronunciation': w.pronunciation,
        'topic': Topic.query.get(w.topic_id).name if w.topic_id else '',
    } for w in words]
    df = pd.DataFrame(data)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='dictiown.csv')

@app.route('/import_csv', methods=['POST'])
def import_csv():
    file = request.files.get('csv_file')
    if file:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            topic = Topic.query.filter_by(name=row.get('topic'), user_id=None).first()
            if not topic and row.get('topic'):
                topic = Topic(name=row['topic'])
                db.session.add(topic)
                db.session.flush()
            word = Word(
                english=row.get('english'),
                spanish=row.get('spanish'),
                french=row.get('french'),
                italian=row.get('italian'),
                pronunciation=row.get('pronunciation'),
                topic_id=topic.id if topic else None
            )
            db.session.add(word)
        db.session.commit()
        flash('CSV imported successfully!')
    return redirect(url_for('settings'))

@app.route('/add_language', methods=['POST'])
def add_language():
    # Placeholder: Would require DB migration for new language columns
    flash('Feature coming soon!')
    return redirect(url_for('settings'))

@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('image_file')
    word_id = request.form.get('word_id')
    if file and word_id:
        filename = secure_filename(file.filename)
        filepath = f'static/uploads/{filename}'
        pil_img = PILImage.open(file)
        pil_img.save(filepath)
        img = Image(filename=filename, word_id=word_id)
        db.session.add(img)
        db.session.commit()
        flash('Image uploaded!')
    return redirect(url_for('settings'))

@app.route('/word/<int:word_id>')
def word_detail(word_id):
    word = Word.query.get_or_404(word_id)
    return render_template('word_detail.html', word=word)

@app.route('/edit_word/<int:word_id>', methods=['GET', 'POST'])
def edit_word(word_id):
    word = Word.query.get_or_404(word_id)
    topics = Topic.query.filter_by(user_id=None).all()
    if request.method == 'POST':
        word.english = request.form['english']
        word.spanish = request.form['spanish']
        word.french = request.form['french']
        word.italian = request.form['italian']
        word.pronunciation = request.form['pronunciation']
        word.topic_id = request.form['topic_id']
        db.session.commit()
        flash('Word updated!')
        return redirect(url_for('word_detail', word_id=word.id))
    return render_template('add_word.html', word=word, topics=topics)

@app.route('/delete_word/<int:word_id>')
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    flash('Word deleted!')
    return redirect(url_for('index'))

@app.route('/add_note/<int:word_id>', methods=['POST'])
def add_note(word_id):
    word = Word.query.get_or_404(word_id)
    note_content = request.form.get('note')
    if note_content:
        note = Note(content=note_content, word_id=word.id)
        db.session.add(note)
        db.session.commit()
        flash('Note added!')
    return redirect(url_for('word_detail', word_id=word.id))

@app.route('/delete_note/<int:note_id>')
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    word_id = note.word_id
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted!')
    return redirect(url_for('word_detail', word_id=word_id))

@app.route('/add_image/<int:word_id>', methods=['POST'])
def add_image(word_id):
    word = Word.query.get_or_404(word_id)
    file = request.files.get('image')
    if file:
        filename = secure_filename(file.filename)
        filepath = f'static/uploads/{filename}'
        pil_img = PILImage.open(file)
        pil_img.save(filepath)
        img = Image(filename=filename, word_id=word.id)
        db.session.add(img)
        db.session.commit()
        flash('Image added!')
    return redirect(url_for('word_detail', word_id=word.id))

@app.route('/delete_image/<int:img_id>')
def delete_image(img_id):
    img = Image.query.get_or_404(img_id)
    word_id = img.word_id
    db.session.delete(img)
    db.session.commit()
    flash('Image deleted!')
    return redirect(url_for('word_detail', word_id=word_id))

@app.route('/study', methods=['GET', 'POST'])
def study():
    topics = Topic.query.filter_by(user_id=None).all()
    if request.method == 'POST':
        # Handle difficulty rating
        word_id = request.form.get('word_id')
        result = request.form.get('result')
        if word_id and result:
            stat = FlashcardStat.query.filter_by(word_id=word_id).first()
            if not stat:
                stat = FlashcardStat(word_id=word_id, times_reviewed=0, familiarity=0.0)
                db.session.add(stat)
            
            # Initialize times_reviewed if it's None
            if stat.times_reviewed is None:
                stat.times_reviewed = 0
            
            # Initialize familiarity if it's None
            if stat.familiarity is None:
                stat.familiarity = 0.0
                
            stat.times_reviewed = stat.times_reviewed + 1
            stat.last_result = result
            
            if result == 'Easy':
                stat.familiarity = min(1.0, stat.familiarity + 0.2)
            elif result == 'Medium':
                stat.familiarity = stat.familiarity + 0.1
            else:  # Hard
                stat.familiarity = max(0, stat.familiarity - 0.1)
            
            db.session.commit()

        # Get next word from session's word list
        remaining_words = session.get('study_words', [])
        if remaining_words:
            word_id = remaining_words.pop(0)
            session['study_words'] = remaining_words
            word = Word.query.get(word_id)
        else:
            word = None
            session.pop('study_words', None)
    else:
        # Setup new study session
        topic_id = request.args.get('topic_id', 'all')
        difficulty = request.args.get('difficulty', 'all')
        num_words = min(100, int(request.args.get('num_words', 10)))
        
        # Query words based on filters
        query = Word.query
        if topic_id != 'all':
            query = query.filter_by(topic_id=topic_id)
        
        words = query.all()
        if difficulty != 'all':
            # Filter by difficulty using FlashcardStats
            stats = FlashcardStat.query.filter_by(last_result=difficulty).all()
            word_ids = [s.word_id for s in stats]
            words = [w for w in words if w.id in word_ids]
        
        # Randomly select words up to num_words
        if words:
            selected_words = random.sample(words, min(len(words), num_words))
            word = selected_words[0] if selected_words else None
            
            # Store remaining words in session
            if len(selected_words) > 1:
                session['study_words'] = [w.id for w in selected_words[1:]]
            else:
                session.pop('study_words', None)
        else:
            word = None
            session.pop('study_words', None)

    return render_template('study.html', 
                         topics=topics,
                         word=word,
                         started=bool(request.args.get('topic_id')),
                         selected_topic=request.args.get('topic_id'),
                         selected_difficulty=request.args.get('difficulty'),
                         num_words=request.args.get('num_words', 10))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True) 