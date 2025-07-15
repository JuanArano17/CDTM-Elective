
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
from datetime import datetime
import uuid

# --- Language Support ---
languages = {
    "en": {
        "app_title": "📚 Bookish",
        "home": "🏠 Home",
        "library": "📚 Library",
        "tbr": "📖 TBR List",
        "stats": "📊 Stats",
        "settings": "⚙️ Settings",
        "register_book": "Register Book",
        "edit_book": "Edit Book",
        "delete_book": "Delete Book",
        "title": "Title",
        "author": "Author",
        "genre": "Genre",
        "stars": "Stars",
        "comments": "Comments (max 200 words)",
        "date_read": "Date Read",
        "cover_image": "Cover Image (optional)",
        "add_book": "Add Book",
        "tbr_title": "Book Title",
        "tbr_author": "Author",
        "tbr_notes": "Notes (max 100 words)",
        "tbr_priority": "Priority",
        "mark_as_read": "Mark as Read",
        "no_books": "No books registered yet.",
        "no_tbr": "No books in TBR list.",
        "total_books": "Total Books",
        "avg_rating": "Average Rating",
        "favorite_genre": "Favorite Genre",
        "books_this_month": "Books This Month",
        "books_this_year": "Books This Year",
        "monthly_trend": "Monthly Reading Trend",
        "genre_diversity": "Genre Diversity",
        "top_authors": "Top Authors",
        "recent_books": "Recent Books",
        "top_rated": "Top Rated Books",
        "dashboard_summary": "Dashboard Summary",
        "add_tbr": "Add to TBR",
        "remove": "Remove",
        "edit": "Edit",
        "save": "Save",
        "cancel": "Cancel",
        "sort_by": "Sort by",
        "rating_desc": "Rating (High-Low)",
        "date_desc": "Date Read (Newest)",
        "title_asc": "Title (A-Z)",
        "title_desc": "Title (Z-A)",
        "search_books": "Search Books",
        "filter_by_genre": "Filter by Genre",
        "all_genres": "All Genres",
        "all_ratings": "All Ratings",
        "filter_by_rating": "Filter by Rating",
        "tbr_list": "TBR List",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "language": "Language",
        "drag_drop": "Drag and drop to reorder TBR priority (use arrows)",
        "top_book": "Top Book"
    },
    "es": {
        "app_title": "📚 Bookish",
        "home": "🏠 Inicio",
        "library": "📚 Biblioteca",
        "tbr": "📖 Por Leer",
        "stats": "📊 Estadísticas",
        "settings": "⚙️ Configuración",
        "register_book": "Registrar Libro",
        "edit_book": "Editar Libro",
        "delete_book": "Eliminar Libro",
        "title": "Título",
        "author": "Autor",
        "genre": "Género",
        "stars": "Estrellas",
        "comments": "Comentarios (máx 200 palabras)",
        "date_read": "Fecha de Lectura",
        "cover_image": "Imagen de Portada (opcional)",
        "add_book": "Agregar Libro",
        "tbr_title": "Título del Libro",
        "tbr_author": "Autor",
        "tbr_notes": "Notas (máx 100 palabras)",
        "tbr_priority": "Prioridad",
        "mark_as_read": "Marcar como Leído",
        "no_books": "No hay libros registrados aún.",
        "no_tbr": "No hay libros en la lista TBR.",
        "total_books": "Total de Libros",
        "avg_rating": "Calificación Promedio",
        "favorite_genre": "Género Favorito",
        "books_this_month": "Libros Este Mes",
        "books_this_year": "Libros Este Año",
        "monthly_trend": "Tendencia Mensual de Lectura",
        "genre_diversity": "Diversidad de Géneros",
        "top_authors": "Autores Principales",
        "recent_books": "Libros Recientes",
        "top_rated": "Libros Mejor Calificados",
        "dashboard_summary": "Resumen del Dashboard",
        "add_tbr": "Agregar a TBR",
        "remove": "Eliminar",
        "edit": "Editar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "sort_by": "Ordenar por",
        "rating_desc": "Calificación (Alta-Baja)",
        "date_desc": "Fecha de Lectura (Más Reciente)",
        "title_asc": "Título (A-Z)",
        "title_desc": "Título (Z-A)",
        "search_books": "Buscar Libros",
        "filter_by_genre": "Filtrar por Género",
        "all_genres": "Todos los Géneros",
        "all_ratings": "Todas las Calificaciones",
        "filter_by_rating": "Filtrar por Calificación",
        "tbr_list": "Por Leer",
        "high": "Alta",
        "medium": "Media",
        "low": "Baja",
        "language": "Idioma",
        "drag_drop": "Arrastra y suelta para reordenar la prioridad TBR (usa flechas)",
        "top_book": "Libro Destacado"
    }
}

# --- Session State Initialization ---
def init_state():
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'books' not in st.session_state:
        st.session_state.books = []
    if 'tbr_list' not in st.session_state:
        st.session_state.tbr_list = []
    if 'editing_book' not in st.session_state:
        st.session_state.editing_book = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'genre_filter' not in st.session_state:
        st.session_state.genre_filter = None

init_state()
lang = languages[st.session_state.language]

# --- Sidebar Navigation ---
st.sidebar.title(lang['app_title'])
st.sidebar.selectbox(
    lang['language'],
    options=['en', 'es'],
    format_func=lambda x: 'English' if x == 'en' else 'Español',
    key='language',
    on_change=lambda: st.rerun()
)
page = st.sidebar.radio(
    "Navigation",
    ['home', 'library', 'tbr', 'stats', 'settings'],
    format_func=lambda x: lang[x],
    key='page_selector'
)
st.session_state.current_page = page

# --- Home Page ---
def home_page():
    st.header(lang['dashboard_summary'])
    if not st.session_state.books:
        st.info(lang['no_books'])
        return
    # Pie chart by genre with click-to-filter
    genre_counts = pd.Series([b['genre'] for b in st.session_state.books]).value_counts()
    fig = px.pie(values=genre_counts.values, names=genre_counts.index, title=lang['genre_diversity'])
    selected = st.plotly_chart(fig, use_container_width=True)
    st.write(f"_{lang['filter_by_genre']}_")
    genre_clicked = st.selectbox(lang['genre'], [lang['all_genres']] + list(genre_counts.index))
    if genre_clicked != lang['all_genres']:
        filtered_books = [b for b in st.session_state.books if b['genre'] == genre_clicked]
    else:
        filtered_books = st.session_state.books
    # Genre cards
    st.subheader(lang['genre_diversity'])
    cols = st.columns(min(4, len(genre_counts)))
    for i, genre in enumerate(genre_counts.index):
        with cols[i % len(cols)]:
            books_in_genre = [b for b in st.session_state.books if b['genre'] == genre]
            avg_rating = sum(b['stars'] for b in books_in_genre) / len(books_in_genre)
            top_book = sorted(books_in_genre, key=lambda x: (-x['stars'], x['date_read'], -len(x['comments'])))[0]
            st.metric(f"{genre}", f"{len(books_in_genre)} {lang['total_books']}")
            st.write(f"{lang['avg_rating']}: {avg_rating:.1f} ⭐")
            st.write(f"{lang['top_book']}: {top_book['title']}")
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(lang['total_books'], len(st.session_state.books))
    with col2:
        avg_rating = sum(book['stars'] for book in st.session_state.books) / len(st.session_state.books)
        st.metric(lang['avg_rating'], f"{avg_rating:.1f} ⭐")
    with col3:
        genres = [book['genre'] for book in st.session_state.books]
        fav_genre = max(set(genres), key=genres.count)
        st.metric(lang['favorite_genre'], fav_genre)
    # Recent books
    st.subheader(lang['recent_books'])
    for book in sorted(filtered_books, key=lambda x: x['date_read'], reverse=True)[:5]:
        st.write(f"**{book['title']}** by {book['author']} ({book['date_read']}) — {'⭐'*book['stars']}")

# --- Library Page ---
def library_page():
    st.header(lang['library'])
    # Register/Edit Book
    with st.expander(lang['register_book']):
        with st.form('add_book_form'):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input(lang['title'])
                author = st.text_input(lang['author'])
            with col2:
                genre = st.selectbox(lang['genre'], [
                    'Fiction', 'Non-Fiction', 'Mystery', 'Romance', 'Sci-Fi', 
                    'Fantasy', 'Biography', 'History', 'Self-Help', 'Poetry',
                    'Thriller', 'Horror', 'Adventure', 'Classic', 'Contemporary'
                ])
                stars = st.slider(lang['stars'], 1, 5, 3)
            comments = st.text_area(lang['comments'], max_chars=200)
            date_read = st.date_input(lang['date_read'], value=datetime.now().date())
            cover_image = st.file_uploader(lang['cover_image'], type=['jpg', 'jpeg', 'png'])
            submitted = st.form_submit_button(lang['add_book'])
            if submitted and title and author:
                book = {
                    'id': str(uuid.uuid4()),
                    'title': title,
                    'author': author,
                    'genre': genre,
                    'stars': stars,
                    'comments': comments,
                    'date_read': date_read.strftime('%Y-%m-%d'),
                    'cover_image': cover_image.getvalue() if cover_image else None
                }
                st.session_state.books.append(book)
                st.success(lang['add_book'])
                st.rerun()
    # Pie chart by genre
    if st.session_state.books:
        genre_counts = pd.Series([b['genre'] for b in st.session_state.books]).value_counts()
        fig = px.pie(values=genre_counts.values, names=genre_counts.index, title=lang['genre_diversity'])
        st.plotly_chart(fig, use_container_width=True)
    # Book list with sorting and filtering
    st.subheader(lang['library'])
    sort_option = st.selectbox(lang['sort_by'], [
        lang['rating_desc'], lang['date_desc'], lang['title_asc'], lang['title_desc']
    ])
    genre_options = [lang['all_genres']] + sorted(set(b['genre'] for b in st.session_state.books))
    genre_filter = st.selectbox(lang['filter_by_genre'], genre_options)
    search = st.text_input(lang['search_books'])
    books = st.session_state.books
    if genre_filter != lang['all_genres']:
        books = [b for b in books if b['genre'] == genre_filter]
    if search:
        books = [b for b in books if search.lower() in b['title'].lower() or search.lower() in b['author'].lower()]
    if sort_option == lang['rating_desc']:
        books = sorted(books, key=lambda x: (-x['stars'], x['date_read'], -len(x['comments'])))
    elif sort_option == lang['date_desc']:
        books = sorted(books, key=lambda x: x['date_read'], reverse=True)
    elif sort_option == lang['title_asc']:
        books = sorted(books, key=lambda x: x['title'])
    elif sort_option == lang['title_desc']:
        books = sorted(books, key=lambda x: x['title'], reverse=True)
    for book in books:
        with st.expander(f"{'⭐'*book['stars']} {book['title']} by {book['author']}"):
            st.write(f"**{lang['genre']}:** {book['genre']}")
            st.write(f"**{lang['date_read']}:** {book['date_read']}")
            st.write(f"**{lang['comments']}:** {book['comments']}")
            if book['cover_image']:
                st.image(Image.open(BytesIO(book['cover_image'])), width=100)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(lang['edit'], key=f"edit_{book['id']}"):
                    st.session_state.editing_book = book
            with col2:
                if st.button(lang['delete_book'], key=f"delete_{book['id']}"):
                    st.session_state.books = [b for b in st.session_state.books if b['id'] != book['id']]
                    st.success(lang['delete_book'])
                    st.rerun()

# --- TBR Page ---
def tbr_page():
    st.header(lang['tbr_list'])
    with st.form('tbr_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            tbr_title = st.text_input(lang['tbr_title'])
        with col2:
            tbr_author = st.text_input(lang['tbr_author'])
        with col3:
            tbr_priority = st.selectbox(lang['tbr_priority'], [lang['high'], lang['medium'], lang['low']])
        tbr_notes = st.text_area(lang['tbr_notes'], max_chars=100)
        tbr_submitted = st.form_submit_button(lang['add_tbr'])
        if tbr_submitted and tbr_title and tbr_author:
            tbr_book = {
                'id': str(uuid.uuid4()),
                'title': tbr_title,
                'author': tbr_author,
                'priority': tbr_priority,
                'notes': tbr_notes
            }
            st.session_state.tbr_list.append(tbr_book)
            st.success(lang['add_tbr'])
            st.rerun()
    # Drag-and-drop reordering (simulated with up/down buttons)
    st.write(f"_{lang['drag_drop']}_")
    if st.session_state.tbr_list:
        priority_order = {lang['high']: 3, lang['medium']: 2, lang['low']: 1}
        sorted_tbr = sorted(st.session_state.tbr_list, key=lambda x: priority_order[x['priority']], reverse=True)
        for idx, book in enumerate(sorted_tbr):
            with st.expander(f"{book['title']} by {book['author']} ({book['priority']})"):
                st.write(f"**{lang['tbr_notes']}:** {book['notes']}")
                col1, col2, col3 = st.columns([1,1,2])
                with col1:
                    if idx > 0 and st.button("⬆️", key=f"up_{book['id']}"):
                        sorted_tbr[idx-1], sorted_tbr[idx] = sorted_tbr[idx], sorted_tbr[idx-1]
                        st.session_state.tbr_list = sorted_tbr
                        st.rerun()
                with col2:
                    if idx < len(sorted_tbr)-1 and st.button("⬇️", key=f"down_{book['id']}"):
                        sorted_tbr[idx+1], sorted_tbr[idx] = sorted_tbr[idx], sorted_tbr[idx+1]
                        st.session_state.tbr_list = sorted_tbr
                        st.rerun()
                with col3:
                    if st.button(lang['mark_as_read'], key=f"read_{book['id']}"):
                        new_book = {
                            'id': str(uuid.uuid4()),
                            'title': book['title'],
                            'author': book['author'],
                            'genre': 'TBR',
                            'stars': 0,
                            'comments': book['notes'],
                            'date_read': datetime.now().strftime('%Y-%m-%d'),
                            'cover_image': None
                        }
                        st.session_state.books.append(new_book)
                        st.session_state.tbr_list = [b for b in st.session_state.tbr_list if b['id'] != book['id']]
                        st.success(lang['mark_as_read'])
                        st.rerun()
                    if st.button(lang['remove'], key=f"remove_tbr_{book['id']}"):
                        st.session_state.tbr_list = [b for b in st.session_state.tbr_list if b['id'] != book['id']]
                        st.rerun()
    else:
        st.info(lang['no_tbr'])

# --- Stats Page ---
def stats_page():
    st.header(lang['stats'])
    if not st.session_state.books:
        st.info(lang['no_books'])
        return
    df = pd.DataFrame(st.session_state.books)
    # Pie chart by genre
    genre_counts = df['genre'].value_counts()
    fig_pie = px.pie(values=genre_counts.values, names=genre_counts.index, title=lang['genre_diversity'])
    st.plotly_chart(fig_pie, use_container_width=True)
    # Line chart: books per month
    df['date_read'] = pd.to_datetime(df['date_read'])
    df['month'] = df['date_read'].dt.to_period('M')
    books_per_month = df.groupby('month').size()
    fig_line = px.line(x=books_per_month.index.astype(str), y=books_per_month.values, title=lang['monthly_trend'])
    st.plotly_chart(fig_line, use_container_width=True)
    # Bar chart: books per year
    df['year'] = df['date_read'].dt.year
    books_per_year = df.groupby('year').size()
    fig_bar = px.bar(x=books_per_year.index, y=books_per_year.values, title=lang['books_this_year'])
    st.plotly_chart(fig_bar, use_container_width=True)
    # Radar chart: genre diversity
    genre_counts = df['genre'].value_counts()
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=genre_counts.values,
        theta=genre_counts.index,
        fill='toself'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, title=lang['genre_diversity'])
    st.plotly_chart(fig_radar, use_container_width=True)

# --- Settings Page ---
def settings_page():
    st.header(lang['settings'])
    st.write("Multi-language and multi-platform support enabled. You can switch language in the sidebar.")

# --- Main App ---
if st.session_state.current_page == 'home':
    home_page()
elif st.session_state.current_page == 'library':
    library_page()
elif st.session_state.current_page == 'tbr':
    tbr_page()
elif st.session_state.current_page == 'stats':
    stats_page()
elif st.session_state.current_page == 'settings':
    settings_page()
