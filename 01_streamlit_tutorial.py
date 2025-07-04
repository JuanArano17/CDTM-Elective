import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import time
from PIL import Image
import io

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Streamlit Showcase",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': 'https://github.com/streamlit/streamlit/issues',
        'About': "This is a comprehensive Streamlit showcase!"
    }
)

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.title("🎯 Streamlit Showcase")
st.sidebar.write("Select a section to explore:")

page = st.sidebar.selectbox(
    "Choose a section:", 
    [ 
        "🏠 Home", 
        "📝 1. Text Elements", 
        "🎮 2. Input Widgets",
        "📐 3. Layout & Containers",
        "📊 4. Data Display",
        "📈 5. Charts & Visualizations", 
        "🎵 6. Media Elements",
        "⚠️ 7. Status Elements",
        "🔄 8. Control Flow",
        "💾 9. Caching & Session State",
        "📝 10. Forms",
        "📑 11. Multi-page Apps",
        "🎨 12. Custom Styling",
        "⚡ 13. Advanced Features"
    ]
)

# Main title
st.title("🎯 Streamlit Complete Showcase")

# =============================================================================
# PAGE CONTENT BASED ON SELECTION
# =============================================================================

if page == "🏠 Home":
    st.header("Welcome to the Streamlit Showcase!")
    st.write("""
    This comprehensive demo showcases all major Streamlit functionalities organized into different sections.
    Use the sidebar to navigate between different features and see how they work.
    """)
    
    st.subheader("📋 What you'll find here:")
    st.markdown("""
    - **Text Elements**: Different ways to display text, markdown, code, and LaTeX
    - **Input Widgets**: All types of user input controls
    - **Layout & Containers**: Columns, tabs, expanders, and containers
    - **Data Display**: Tables, dataframes, metrics, and JSON
    - **Charts & Visualizations**: Built-in charts and Plotly integration
    - **Media Elements**: Images, audio, and video support
    - **Status Elements**: Messages, progress bars, and notifications
    - **Control Flow**: Conditional execution and app flow control
    - **Caching & Session State**: Performance optimization and state management
    - **Forms**: Form handling and validation
    - **Multi-page Apps**: How to create apps with multiple pages
    - **Custom Styling**: CSS and HTML customization
    - **Advanced Features**: Dynamic updates and advanced functionality
    """)
    
    st.info("👈 Use the sidebar to explore each section!")

elif page == "📝 1. Text Elements":
    st.header("1. Text Elements")
    st.subheader("Different ways to display text")

    # Regular text
    st.write("This is regular text using st.write()")
    st.text("This is monospace text using st.text()")

    # Markdown
    st.markdown("**Bold text**, *italic text*, and `code text`")
    st.markdown("""
    ### Markdown list:
    - Item 1
    - Item 2
    - Item 3
    """)

    # LaTeX
    st.latex(r"e^{i\pi} + 1 = 0")

    # Code
    st.code("""
def hello_world():
    print("Hello, Streamlit!")
    """, language="python")

    # Captions
    st.caption("This is a small caption text")

elif page == "🎮 2. Input Widgets":
    st.header("2. Input Widgets")

    # Text inputs
    name = st.text_input("Enter your name:", "Default value")
    text_area = st.text_area("Enter multiple lines:", "Default\ntext")
    password = st.text_input("Enter password:", type="password")

    # Number inputs
    number_input = st.number_input("Enter a number:", min_value=0, max_value=100, value=50)
    slider = st.slider("Select a range:", 0, 100, (25, 75))
    single_slider = st.slider("Single value:", 0, 100, 50)

    # Select inputs
    selectbox = st.selectbox("Choose an option:", ["Option 1", "Option 2", "Option 3"])
    multiselect = st.multiselect("Choose multiple:", ["A", "B", "C", "D"], default=["A", "B"])
    radio = st.radio("Pick one:", ["Radio 1", "Radio 2", "Radio 3"])

    # Boolean inputs
    checkbox = st.checkbox("Check this box")
    toggle = st.toggle("Toggle this")

    # Date and time
    date_input = st.date_input("Pick a date:", datetime.now().date())
    time_input = st.time_input("Pick a time:", datetime.now().time())

    # File uploader
    uploaded_file = st.file_uploader("Upload a file:", type=['csv', 'txt', 'png', 'jpg'])

    # Color picker
    color = st.color_picker("Pick a color:", "#FF0000")

    # Button
    if st.button("Click me!"):
        st.success("Button clicked!")

    # Download button
    st.download_button(
        label="Download sample data",
        data="Sample,Data\n1,A\n2,B\n3,C",
        file_name="sample.csv",
        mime="text/csv"
    )

elif page == "📐 3. Layout & Containers":
    st.header("3. Layout and Containers")

    # Columns
    st.subheader("Columns")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Column 1")
        st.button("Button 1")
    with col2:
        st.write("Column 2")
        st.button("Button 2")
    with col3:
        st.write("Column 3")
        st.button("Button 3")

    # Columns with different widths
    st.subheader("Columns with different widths")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("Wide column (2/3)")
    with col2:
        st.write("Narrow column (1/3)")

    # Tabs
    st.subheader("Tabs")
    tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    with tab1:
        st.write("Content of tab 1")
    with tab2:
        st.write("Content of tab 2")
    with tab3:
        st.write("Content of tab 3")

    # Expander
    st.subheader("Expander")
    with st.expander("Click to expand"):
        st.write("Hidden content here!")
        st.write("More hidden content!")

    # Container
    st.subheader("Container")
    container = st.container()
    container.write("This is inside a container")

elif page == "📊 4. Data Display":
    st.header("4. Data Display")

    # Sample data
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'City': ['New York', 'London', 'Tokyo', 'Paris'],
        'Salary': [50000, 60000, 70000, 55000]
    })

    # Dataframe
    st.subheader("Dataframe")
    st.dataframe(df)

    # Data editor (editable table)
    st.subheader("Editable Data")
    edited_df = st.data_editor(df)

    # Table (static)
    st.subheader("Static Table")
    st.table(df.head(2))

    # Metrics
    st.subheader("Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Employees", "4", "1")
    col2.metric("Average Age", "29.5", "2.5")
    col3.metric("Average Salary", "$58,750", "$5,000")
    col4.metric("Cities", "4", "0")

    # JSON
    st.subheader("JSON Display")
    st.json({
        "name": "John Doe",
        "age": 30,
        "languages": ["Python", "JavaScript", "Go"]
    })

elif page == "📈 5. Charts & Visualizations":
    st.header("5. Charts and Visualizations")

    # Sample chart data
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )

    # Line chart
    st.subheader("Line Chart")
    st.line_chart(chart_data)

    # Area chart
    st.subheader("Area Chart")
    st.area_chart(chart_data)

    # Bar chart
    st.subheader("Bar Chart")
    st.bar_chart(chart_data)

    # Scatter chart
    st.subheader("Scatter Chart")
    scatter_data = pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'size': np.random.randint(10, 100, 100)
    })
    st.scatter_chart(scatter_data, x='x', y='y', size='size')

    # Plotly charts
    st.subheader("Plotly Charts")
    fig = px.scatter(scatter_data, x='x', y='y', size='size', 
                     title="Interactive Plotly Scatter Plot")
    st.plotly_chart(fig, use_container_width=True)

    # Map
    st.subheader("Map")
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
        columns=['lat', 'lon']
    )
    st.map(map_data)

elif page == "🎵 6. Media Elements":
    st.header("6. Media Elements")
    
    st.info("Media elements require actual files to display. Here are the functions you would use:")
    
    st.code("""
# Image
st.image("path/to/image.jpg", caption="Sample Image", width=300)

# Audio
st.audio("path/to/audio.mp3")

# Video
st.video("path/to/video.mp4")
    """, language="python")

elif page == "⚠️ 7. Status Elements":
    st.header("7. Status Elements")

    # Success, info, warning, error
    st.success("This is a success message!")
    st.info("This is an info message!")
    st.warning("This is a warning message!")
    st.error("This is an error message!")

    # Balloons and snow
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Show balloons"):
            st.balloons()
    with col2:
        if st.button("Show snow"):
            st.snow()

    # Progress bar
    st.subheader("Progress Bar")
    if st.button("Run Progress Demo"):
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.01)

    # Spinner
    st.subheader("Spinner")
    if st.button("Show Spinner"):
        with st.spinner('Wait for it...'):
            time.sleep(2)
        st.success('Done!')

elif page == "🔄 8. Control Flow":
    st.header("8. Control Flow")

    # Stop execution
    name = st.text_input("Enter your name:")
    if not name:
        st.warning("Please enter your name above!")
        st.stop()

    st.write(f"Hello, {name}!")
    st.success("This message only appears after you enter your name!")

elif page == "💾 9. Caching & Session State":
    st.header("9. Caching and Session State")

    # Cached function
    @st.cache_data
    def expensive_computation(n):
        time.sleep(1)  # Simulate expensive computation
        return sum(range(n))

    st.subheader("Caching Demo")
    n = st.slider("Select n for computation:", 1, 1000, 100)
    result = expensive_computation(n)
    st.write(f"Sum of 1 to {n} = {result}")
    st.info("This computation is cached - try changing the slider back and forth!")

    # Session state
    st.subheader("Session State Demo")
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Increment"):
            st.session_state.counter += 1
    with col2:
        if st.button("Decrement"):
            st.session_state.counter -= 1
    with col3:
        if st.button("Reset"):
            st.session_state.counter = 0

    st.write(f"Counter value: {st.session_state.counter}")

elif page == "📝 10. Forms":
    st.header("10. Forms")

    # Form
    with st.form("my_form"):
        st.write("Inside the form")
        name = st.text_input("Name:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f"Submitted: {name}, age {age}")

elif page == "📑 11. Multi-page Apps":
    st.header("11. Multi-page App Navigation")
    st.write("To create a multi-page app, create multiple .py files in a 'pages' folder:")
    st.code("""
# Main app: streamlit_app.py
import streamlit as st
st.title("Home Page")

# pages/1_📊_Dashboard.py
import streamlit as st
st.title("Dashboard")

# pages/2_⚙️_Settings.py
import streamlit as st
st.title("Settings")
    """)

elif page == "🎨 12. Custom Styling":
    st.header("12. Custom Styling")

    # Custom CSS
    st.markdown("""
    <style>
    .custom-text {
        color: red;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="custom-text">This text has custom styling!</p>', 
                unsafe_allow_html=True)

elif page == "⚡ 13. Advanced Features":
    st.header("13. Advanced Features")

    # Empty placeholder that can be updated
    st.subheader("Dynamic Content Update")
    if st.button("Update Content"):
        placeholder = st.empty()
        for i in range(5):
            placeholder.text(f"Updating... {i}")
            time.sleep(1)
        placeholder.text("Done updating!")

    # Rerun button
    st.subheader("App Rerun")
    if st.button("Rerun app"):
        st.rerun()

# =============================================================================
# SIDEBAR FOOTER
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎉 Streamlit Showcase")
st.sidebar.markdown("Explore each section to see different functionalities!")
st.sidebar.markdown("[Streamlit Docs](https://docs.streamlit.io/)")

