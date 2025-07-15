import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from PIL import Image
import json
import os
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.neighbors import NearestNeighbors
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- THEME & FONT INJECTION ---
def get_secondary_color():
    return st.session_state.get('secondary_color', '#6f42c1')

def set_secondary_color(color):
    st.session_state['secondary_color'] = color

secondary_color = get_secondary_color()

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');
    html, body, [class*="css"]  {{
        font-family: 'Montserrat', sans-serif;
        background-color: #181028;
        color: #F3F3F3;
    }}
    /* Center main content and set max width */
    .main .block-container {{
        max-width: 900px;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 700;
        letter-spacing: 0.01em;
        color: #fff;
        margin-bottom: 0.5em;
    }}
    /* Subtle card style for widgets */
    .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div>div>input, .stSlider>div, .stMultiSelect>div {{
        border-radius: 18px !important;
        background: #232136 !important;
        color: #fff !important;
        border: 1.5px solid {secondary_color} !important;
        box-shadow: 0 2px 12px 0 rgba(0,0,0,0.10);
        transition: box-shadow 0.2s, border 0.2s;
    }}
    .stButton>button:hover, .stTextInput>div>div>input:focus, .stSelectbox>div>div>div>input:focus, .stSlider>div:focus, .stMultiSelect>div:focus {{
        border: 1.5px solid {secondary_color} !important;
        box-shadow: 0 4px 24px 0 {secondary_color}33;
    }}
    /* Sidebar and side menu backgrounds */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(135deg, {secondary_color} 60%, #1a1124 100%) !important;
        color: #fff !important;
    }}
    .stSidebar {{
        background: linear-gradient(135deg, {secondary_color} 60%, #1a1124 100%) !important;
        color: #fff !important;
    }}
    .stOptionMenu .nav-link {{
        color: #fff !important;
        background: rgba(45, 19, 59, 0.7) !important;
        border-radius: 16px !important;
        margin-bottom: 8px;
        transition: background 0.2s;
    }}
    .stOptionMenu .nav-link.active {{
        background: linear-gradient(90deg, {secondary_color} 0%, #a259f7 100%) !important;
        color: #fff !important;
        box-shadow: 0 0 10px {secondary_color};
    }}
    .stOptionMenu .nav-link:hover {{
        background: linear-gradient(90deg, {secondary_color} 0%, #2d133b 100%) !important;
        color: #fff !important;
    }}
    /* Playlist cards and grid */
    div[data-testid="stHorizontalBlock"] > div > div > div {{
        background: #232136 !important;
        border-radius: 18px !important;
        box-shadow: 0 2px 12px 0 {secondary_color}33 !important;
        border: 1.5px solid {secondary_color} !important;
        transition: box-shadow 0.2s, border 0.2s;
    }}
    div[data-testid="stHorizontalBlock"] > div > div > div:hover {{
        box-shadow: 0 4px 24px 0 {secondary_color}99 !important;
        border: 2px solid {secondary_color} !important;
    }}
    /* Expander header */
    .streamlit-expanderHeader {{
        background: #232136 !important;
        color: #fff !important;
        border-radius: 12px !important;
        border: 1.5px solid {secondary_color} !important;
        font-weight: 600;
    }}
    /* Slider track and handle */
    .stSlider > div[data-baseweb="slider"] > div > div {{
        background: {secondary_color} !important;
    }}
    .stSlider .rc-slider-handle {{
        background: {secondary_color} !important;
        border: 2px solid #fff !important;
    }}
    /* Dataframe/table style */
    .stDataFrame {{
        background: #232136 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 12px 0 {secondary_color}33 !important;
    }}
    .stDataFrame thead tr th {{
        background: {secondary_color} !important;
        color: #fff !important;
        font-weight: 700;
        font-size: 1.05em;
        border-bottom: 2px solid #232136 !important;
    }}
    .stDataFrame tbody tr {{
        background: #232136 !important;
        color: #fff !important;
    }}
    .stDataFrame tbody tr:hover {{
        background: {secondary_color}22 !important;
    }}
    /* Section spacing */
    .block-container > div {{
        margin-bottom: 2.5rem;
    }}
    /* Responsive tweaks */
    @media (max-width: 1000px) {{
        .main .block-container {{
            max-width: 98vw;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- DATA LOADING & NORMALIZATION ---
@st.cache_data
def load_and_normalize_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Normalize songs, artists, genres, moods
    songs = [x for x in data if x['model'] == 'app.song']
    artists = {x['pk']: x['fields'] for x in data if x['model'] == 'app.artist'}
    genres = {x['pk']: x['fields']['name'] for x in data if x['model'] == 'app.genre'}
    moods = {x['pk']: x['fields']['name'] for x in data if x['model'] == 'app.mood'}
    # Flatten song fields
    song_rows = []
    for s in songs:
        f = s['fields']
        song_rows.append({
            'title': f['title'],
            'artist_id': f['artist'],
            'artist': artists.get(f['artist'], {}).get('name', 'Unknown'),
            'genres': [genres.get(g, str(g)) for g in f.get('genres', [])],
            'bpm': f.get('bpm'),
            'moods': [moods.get(m, str(m)) for m in f.get('moods', [])],
            'language': f.get('language'),
            'year': f.get('year'),
            'tags': f.get('tags', []),
        })
    df = pd.DataFrame(song_rows)
    return df, artists, genres, moods

# Path to the database
DB_PATH = 'moodsic_songs_fixture.json'

# Load data
songs_df, artists_dict, genres_dict, moods_dict = load_and_normalize_data(DB_PATH)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    selected = option_menu(
        "Moodsic",
        ["Landing", "Filter Songs", "Song Likeness", "Playlist Maker", "Mood Playlist", "Profile", "Config", "Upload Playlist"],
        icons=["house", "filter", "search", "music-note-list", "emoji-smile", "person-circle", "gear", "cloud-upload"],
        menu_icon="music-note-beamed",
        default_index=0,
        orientation="vertical"
    )

def autocomplete_search_bar(label, df, key="search_input"):  # df must have 'title' and 'artist'
    # Get user input
    user_input = st.text_input(label, key=key)
    matches = []
    if user_input:
        # Case-insensitive search in title or artist
        matches = df[df['title'].str.contains(user_input, case=False) | df['artist'].str.contains(user_input, case=False)]
        matches = matches[['title', 'artist']].drop_duplicates().head(10)
        if not matches.empty:
            # Custom dropdown
            st.markdown('<div style="position:relative;z-index:1000;">', unsafe_allow_html=True)
            option = st.radio(
                "",
                [f"{row['title']} - {row['artist']}" for _, row in matches.iterrows()],
                key=f"{key}_dropdown",
                label_visibility="collapsed",
                index=0
            )
            st.markdown('</div>', unsafe_allow_html=True)
            return user_input, option
    return user_input, None

# --- PAGE ROUTING ---
def landing_page():
    st.title("Moodsic 🎵 Playlist Maker")
    st.write("Welcome to Moodsic! Find, filter, and create playlists based on your mood and taste.")
    published = get_published_playlists()
    featured = published[:6] if published else []
    # --- Playlist Detail View ---
    if 'selected_playlist_idx' in st.session_state:
        idx = st.session_state['selected_playlist_idx']
        pl = published[idx]
        st.markdown(f"## {pl['name']}")
        st.write(pl['description'])
        df = pd.DataFrame(pl['songs'])
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("Back to Playlists", key="back_to_playlists"):
            del st.session_state['selected_playlist_idx']
        return
    # --- Search bar (already implemented) ---
    st.subheader("Search for a song")
    all_songs = get_all_songs_df()
    user_input, selected_song = autocomplete_search_bar("Type a song or artist...", all_songs, key="landing_search")
    if selected_song:
        st.success(f"You selected: {selected_song}")
    st.markdown("---")
    # --- Featured Playlists Cards ---
    st.subheader("Featured Playlists")
    if featured:
        cols = st.columns(3)
        for i, pl in enumerate(featured):
            col = cols[i % 3]
            with col:
                st.markdown(f'''
                <div class="playlist-card" style="display: flex; flex-direction: column; align-items: flex-start;">
                    <div class="playlist-card-title">{pl['name']}</div>
                    <div class="playlist-card-desc">{pl['description'][:60] + ('...' if len(pl['description']) > 60 else '')}</div>
                ''', unsafe_allow_html=True)
                if st.button("View", key=f"feat_view_{i}"):
                    st.session_state['selected_playlist_idx'] = i
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No featured playlists yet. Publish some from the Playlist Maker!")
    st.markdown("---")
    # --- Grid of Published Playlists as Cards ---
    st.subheader("Published Playlists")
    grid_per_row = 3
    show_n = st.session_state.get('landing_show_n', 6)
    if published:
        st.markdown('<div class="playlist-card-row">', unsafe_allow_html=True)
        for idx, pl in enumerate(published[:show_n]):
            view_btn = st.button("View", key=f"grid_view_{idx}")
            st.markdown(f'''
            <div class="playlist-card">
                <div class="playlist-card-title">{pl['name']}</div>
                <div class="playlist-card-desc">{pl['description'][:60] + ('...' if len(pl['description']) > 60 else '')}</div>
            </div>
            ''', unsafe_allow_html=True)
            if view_btn:
                st.session_state['selected_playlist_idx'] = idx
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        if show_n < len(published):
            if st.button("Load More Playlists", key="load_more_grid"):
                st.session_state['landing_show_n'] = show_n + 6
    else:
        st.info("No playlists published yet. Publish some from the Playlist Maker!")
    # --- Card CSS ---
    st.markdown(f'''
    <style>
    .playlist-card-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: flex-start;
        margin-bottom: 2rem;
    }}
    .playlist-card {{
        background: #232136;
        border-radius: 18px;
        box-shadow: 0 2px 12px 0 {secondary_color}33;
        border: 1.5px solid {secondary_color};
        min-width: 260px;
        max-width: 300px;
        min-height: 160px;
        padding: 1.2rem 1.2rem 1.5rem 1.2rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        transition: box-shadow 0.2s, border 0.2s;
    }}
    .playlist-card:hover {{
        box-shadow: 0 4px 24px 0 {secondary_color}99;
        border: 2px solid {secondary_color};
    }}
    .playlist-card-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.5rem;
    }}
    .playlist-card-desc {{
        font-size: 1rem;
        color: #d1c4e9;
        margin-bottom: 1.2rem;
        min-height: 2.5em;
    }}
    .playlist-card-btn {{
        background: linear-gradient(90deg, {secondary_color} 0%, #2d133b 100%);
        color: #fff;
        border: none;
        border-radius: 16px;
        padding: 0.5rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 2px 8px 0 {secondary_color}33;
        transition: background 0.2s, box-shadow 0.2s;
    }}
    .playlist-card-btn:hover {{
        background: linear-gradient(90deg, #2d133b 0%, {secondary_color} 100%);
        box-shadow: 0 4px 16px 0 {secondary_color}99;
    }}
    @media (max-width: 1000px) {{
        .playlist-card-row {{
            gap: 1rem;
        }}
        .playlist-card {{
            min-width: 98vw;
            max-width: 98vw;
        }}
    }}
    </style>
    ''', unsafe_allow_html=True)

def filter_songs_page():
    st.header("Filter Songs")
    all_songs = get_all_songs_df()
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            genres = st.multiselect("Genre(s)", options=list(genres_dict.values()), key="filter_genres")
            moods = st.multiselect("Mood(s)", options=list(moods_dict.values()), key="filter_moods")
        with col2:
            artists = st.multiselect("Artist(s)", options=sorted(set(all_songs['artist'])), key="filter_artists")
            language = st.multiselect("Language(s)", options=sorted(set(all_songs['language'])), key="filter_langs")
        with col3:
            bpm_min, bpm_max = int(all_songs['bpm'].min()), int(all_songs['bpm'].max())
            bpm_range = st.slider("BPM Range", min_value=bpm_min, max_value=bpm_max, value=(bpm_min, bpm_max), key="filter_bpm")
            year_min, year_max = int(all_songs['year'].min()), int(all_songs['year'].max())
            year_range = st.slider("Year Range", min_value=year_min, max_value=year_max, value=(year_min, year_max), key="filter_year")
    sort_by = st.selectbox("Sort by", options=["title", "artist", "bpm", "year"], index=0, key="sort_by")
    sort_asc = st.toggle("Ascending", value=True, key="sort_asc")
    filtered = all_songs.copy()
    if genres:
        filtered = filtered[filtered['genres'].apply(lambda x: any(g in x for g in genres))]
    if moods:
        filtered = filtered[filtered['moods'].apply(lambda x: any(m in x for m in moods))]
    if artists:
        filtered = filtered[filtered['artist'].isin(artists)]
    if language:
        filtered = filtered[filtered['language'].isin(language)]
    filtered = filtered[(filtered['bpm'] >= bpm_range[0]) & (filtered['bpm'] <= bpm_range[1])]
    filtered = filtered[(filtered['year'] >= year_range[0]) & (filtered['year'] <= year_range[1])]
    if hasattr(filtered, "sort_values"):
        filtered = filtered.sort_values(by=sort_by, ascending=sort_asc)
    st.markdown("### Results")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, hide_index=True)

def song_likeness_page():
    st.header("Song Likeness Search")
    st.write("Find songs similar to your favorite!")
    all_songs = get_all_songs_df()
    user_input, selected_song = autocomplete_search_bar("Type a song or artist...", all_songs, key="likeness_search")
    if selected_song:
        title, artist = selected_song.split(" - ", 1)
        song_row = all_songs[(all_songs['title'] == title) & (all_songs['artist'] == artist)]
        if not song_row.empty:
            feature_df = all_songs.copy()
            from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
            from sklearn.neighbors import NearestNeighbors
            mlb_genre = MultiLabelBinarizer()
            mlb_mood = MultiLabelBinarizer()
            genre_encoded = mlb_genre.fit_transform(feature_df['genres'])
            mood_encoded = mlb_mood.fit_transform(feature_df['moods'])
            numeric = feature_df[['bpm', 'year']].fillna(0).values
            X = np.hstack([numeric, genre_encoded, mood_encoded])
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            idx = song_row.index[0]
            nn = NearestNeighbors(n_neighbors=6, metric='euclidean')
            nn.fit(X_scaled)
            dists, indices = nn.kneighbors([X_scaled[idx]])
            similar_indices = indices[0][1:]
            similar_songs = feature_df.iloc[similar_indices][['title', 'artist', 'bpm', 'genres', 'moods', 'year']]
            st.markdown("### Similar Songs")
            st.dataframe(similar_songs.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.warning("Song not found in database.")

# Helper: get or create published playlists in session state
def get_published_playlists():
    if 'published_playlists' not in st.session_state:
        st.session_state['published_playlists'] = []
    return st.session_state['published_playlists']

def publish_playlist(playlist, name, description):
    published = get_published_playlists()
    published.append({
        'name': name,
        'description': description,
        'songs': playlist.to_dict('records')
    })
    st.session_state['published_playlists'] = published

def profile_page():
    st.header("Profile")
    # Mock user info
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://ui-avatars.com/api/?name=Moodsic+User&background=6f42c1&color=fff&size=128", width=96)
    with col2:
        st.subheader("Moodsic User")
        st.caption("Music lover. Playlist creator. Moodsic enthusiast.")
    st.markdown("---")
    st.subheader("Published Playlists")
    published = get_published_playlists()
    if published:
        for i, pl in enumerate(published):
            with st.expander(f"{pl['name']}"):
                st.write(pl['description'])
                df = pd.DataFrame(pl['songs'])
                st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No playlists published yet.")

def config_page():
    st.header("Config")
    st.write("Change the secondary color of the web to customize your experience.")
    color_options = {
        'Purple': '#6f42c1',
        'Blue': '#2979ff',
        'Green': '#00c853',
        'Pink': '#e040fb',
        'Orange': '#ff9100',
        'Red': '#ff1744',
    }
    color_name = st.selectbox("Choose a secondary color", list(color_options.keys()),
                              index=list(color_options.values()).index(get_secondary_color()) if get_secondary_color() in color_options.values() else 0)
    if st.button("Apply Color"):
        set_secondary_color(color_options[color_name])
        st.rerun()
    st.markdown(f"<div style='margin-top:16px;'><b>Preview:</b> <span style='background:linear-gradient(90deg,#2d133b,{color_options[color_name]});padding:8px 24px;border-radius:12px;color:#fff;'>This is your new accent!</span></div>", unsafe_allow_html=True)

def upload_playlist_page():
    st.header("Upload Playlist")
    st.write("Download the template, fill it with your songs, and upload to add your playlists to Moodsic!")
    # Template download
    template_df = pd.DataFrame([
        {"title": "Song Title", "artist": "Artist Name", "bpm": 120, "genres": "Trap,Hip-Hop", "moods": "fly,flow", "language": "EN", "year": 2023}
    ])
    st.download_button(
        label="Download CSV Template",
        data=template_df.to_csv(index=False),
        file_name="moodsic_playlist_template.csv",
        mime="text/csv"
    )
    # Upload
    uploaded_file = st.file_uploader("Upload your playlist CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file)
            # Parse genres and moods as lists
            user_df['genres'] = user_df['genres'].apply(lambda x: [g.strip() for g in str(x).split(',')])
            user_df['moods'] = user_df['moods'].apply(lambda x: [m.strip() for m in str(x).split(',')])
            # Fill missing columns
            for col in ['title', 'artist', 'bpm', 'genres', 'moods', 'language', 'year']:
                if col not in user_df:
                    user_df[col] = ''
            st.session_state['user_uploaded_songs'] = user_df
            st.success("Playlist uploaded and merged! All features now include your songs.")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    # Show uploaded songs
    if 'user_uploaded_songs' in st.session_state:
        st.markdown("### Your Uploaded Songs")
        st.dataframe(st.session_state['user_uploaded_songs'], use_container_width=True, hide_index=True)

# --- Use merged songs for all features ---
def get_all_songs_df():
    if 'user_uploaded_songs' in st.session_state:
        merged = pd.concat([songs_df, st.session_state['user_uploaded_songs']], ignore_index=True)
        return merged
    return songs_df

# Update all usages of songs_df to get_all_songs_df() in relevant pages

# --- Add publish button to playlist makers ---
def playlist_publish_ui(playlist, key_prefix):
    st.write("**Select songs to include in your playlist:**")
    # Create options for multiselect: show title and artist for clarity
    song_options = [f"{row['title']} - {row['artist']}" for _, row in playlist.iterrows()]
    sel_key = f"{key_prefix}_selected_songs"
    # Default: all songs selected
    if sel_key not in st.session_state:
        st.session_state[sel_key] = song_options.copy()
    selected_songs = st.multiselect(
        "Songs to include:",
        options=song_options,
        key=sel_key,
        help="Select which songs to include in your playlist."
    )
    # Filter playlist to selected songs
    selected_indices = [song_options.index(s) for s in selected_songs if s in song_options]
    selected_playlist = playlist.iloc[selected_indices] if selected_indices else playlist.iloc[[]]
    st.markdown("### Preview of Selected Songs")
    st.dataframe(selected_playlist.reset_index(drop=True), use_container_width=True, hide_index=True)
    with st.expander("Publish this playlist to your profile?"):
        name = st.text_input("Playlist Name", key=f"{key_prefix}_pub_name")
        desc = st.text_area("Description", key=f"{key_prefix}_pub_desc")
        if st.button("Publish", key=f"{key_prefix}_pub_btn"):
            if name and desc and not selected_playlist.empty:
                publish_playlist(selected_playlist, name, desc)
                st.success("Playlist published to your profile!")
            elif selected_playlist.empty:
                st.warning("Please select at least one song.")
            else:
                st.warning("Please enter a name and description.")

# --- Update playlist_maker_page and mood_playlist_page to allow publishing ---
def playlist_maker_page():
    st.header("Playlist Maker")
    all_songs = get_all_songs_df()
    tab1, tab2 = st.tabs(["By Song", "By Filters"])
    with tab1:
        st.subheader("By Song")
        st.write("Select a song and the number of songs for your playlist. We'll find the best matches!")
        user_input, selected_song = autocomplete_search_bar("Type a song or artist...", all_songs, key="playlist_song_search")
        n_songs = st.slider("Number of songs in playlist", min_value=3, max_value=20, value=10, key="playlist_n")
        if selected_song:
            title, artist = selected_song.split(" - ", 1)
            song_row = all_songs[(all_songs['title'] == title) & (all_songs['artist'] == artist)]
            if not song_row.empty:
                feature_df = all_songs.copy()
                from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
                from sklearn.neighbors import NearestNeighbors
                mlb_genre = MultiLabelBinarizer()
                mlb_mood = MultiLabelBinarizer()
                genre_encoded = mlb_genre.fit_transform(feature_df['genres'])
                mood_encoded = mlb_mood.fit_transform(feature_df['moods'])
                numeric = feature_df[['bpm', 'year']].fillna(0).values
                X = np.hstack([numeric, genre_encoded, mood_encoded])
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                idx = song_row.index[0]
                n_neighbors = min(n_songs + 1, len(feature_df))
                nn = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
                nn.fit(X_scaled)
                dists, indices = nn.kneighbors([X_scaled[idx]])
                playlist_indices = indices[0][1:n_songs+1]
                playlist = feature_df.iloc[playlist_indices][['title', 'artist', 'bpm', 'genres', 'moods', 'year']]
                st.markdown(f"### Playlist ({n_songs} songs similar to '{title}' by {artist})")
                st.dataframe(playlist.reset_index(drop=True), use_container_width=True, hide_index=True)
                playlist_publish_ui(playlist, key_prefix="by_song")
            else:
                st.warning("Song not found in database.")
    with tab2:
        st.subheader("By Filters")
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                genres = st.multiselect("Genre(s)", options=list(genres_dict.values()), key="plf_genres")
                moods = st.multiselect("Mood(s)", options=list(moods_dict.values()), key="plf_moods")
            with col2:
                artists = st.multiselect("Artist(s)", options=sorted(set(all_songs['artist'])), key="plf_artists")
                language = st.multiselect("Language(s)", options=sorted(set(all_songs['language'])), key="plf_langs")
            with col3:
                bpm_min, bpm_max = int(all_songs['bpm'].min()), int(all_songs['bpm'].max())
                bpm_range = st.slider("BPM Range", min_value=bpm_min, max_value=bpm_max, value=(bpm_min, bpm_max), key="plf_bpm")
                year_min, year_max = int(all_songs['year'].min()), int(all_songs['year'].max())
                year_range = st.slider("Year Range", min_value=year_min, max_value=year_max, value=(year_min, year_max), key="plf_year")
        n_songs = st.slider("Number of songs in playlist", min_value=3, max_value=30, value=10, key="plf_n")
        filtered = all_songs.copy()
        if genres:
            filtered = filtered[filtered['genres'].apply(lambda x: any(g in x for g in genres))]
        if moods:
            filtered = filtered[filtered['moods'].apply(lambda x: any(m in x for m in moods))]
        if artists:
            filtered = filtered[filtered['artist'].isin(artists)]
        if language:
            filtered = filtered[filtered['language'].isin(language)]
        filtered = filtered[(filtered['bpm'] >= bpm_range[0]) & (filtered['bpm'] <= bpm_range[1])]
        filtered = filtered[(filtered['year'] >= year_range[0]) & (filtered['year'] <= year_range[1])]
        playlist = filtered.head(n_songs)[['title', 'artist', 'bpm', 'genres', 'moods', 'year']]
        st.markdown(f"### Playlist ({len(playlist)} songs)")
        st.dataframe(playlist.reset_index(drop=True), use_container_width=True, hide_index=True)
        if not playlist.empty:
            playlist_publish_ui(playlist, key_prefix="by_filters")

def mood_playlist_page():
    st.header("Playlist Maker by Mood")
    st.write("Select a mood and get a playlist that matches your vibe!")
    all_songs = get_all_songs_df()
    mood = st.selectbox("Select Mood", options=list(moods_dict.values()), key="mood_select")
    n_songs = st.slider("Number of songs in playlist", min_value=3, max_value=30, value=10, key="mood_n")
    filtered = all_songs[all_songs['moods'].apply(lambda x: mood in x)]
    playlist = filtered.head(n_songs)[['title', 'artist', 'bpm', 'genres', 'moods', 'year']]
    st.markdown(f"### Playlist for mood: {mood} ({len(playlist)} songs)")
    st.dataframe(playlist.reset_index(drop=True), use_container_width=True, hide_index=True)
    if not playlist.empty:
        playlist_publish_ui(playlist, key_prefix=f"by_mood_{mood}")

# --- PAGE DISPATCH ---
if selected == "Landing":
    landing_page()
elif selected == "Filter Songs":
    filter_songs_page()
elif selected == "Song Likeness":
    song_likeness_page()
elif selected == "Playlist Maker":
    playlist_maker_page()
elif selected == "Mood Playlist":
    mood_playlist_page()
elif selected == "Profile":
    profile_page()
elif selected == "Config":
    config_page()
elif selected == "Upload Playlist":
    upload_playlist_page() 