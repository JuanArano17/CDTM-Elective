import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
from streamlit_option_menu import option_menu

# Page config
st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Multi-language support
LANGUAGES = {
    "English": {
        "title": "Finance Tracker",
        "dashboard": "Dashboard",
        "transactions": "Transactions",
        "add_transaction": "Add Transaction",
        "stock_name": "Stock/ETF Name",
        "buy_date": "Buy Date",
        "buy_price": "Buy Price (€)",
        "sell_date": "Sell Date",
        "sell_price": "Sell Price (€)",
        "gain_loss": "Gain/Loss (€)",
        "gain_loss_pct": "Gain/Loss (%)",
        "current_price": "Current Price (€)",
        "variation": "Variation (%)",
        "owned": "Currently Owned",
        "history": "Transaction History",
        "save": "Save",
        "delete": "Delete",
        "edit": "Edit",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "no_transactions": "No transactions found.",
        "date": "Date",
        "price": "Price (€)",
        "actions": "Actions"
    },
    "Spanish": {
        "title": "Rastreador Financiero",
        "dashboard": "Panel Principal",
        "transactions": "Transacciones",
        "add_transaction": "Agregar Transacción",
        "stock_name": "Nombre de Acción/ETF",
        "buy_date": "Fecha de Compra",
        "buy_price": "Precio de Compra (€)",
        "sell_date": "Fecha de Venta",
        "sell_price": "Precio de Venta (€)",
        "gain_loss": "Ganancia/Pérdida (€)",
        "gain_loss_pct": "Ganancia/Pérdida (%)",
        "current_price": "Precio Actual (€)",
        "variation": "Variación (%)",
        "owned": "Actualmente en Cartera",
        "history": "Historial de Transacciones",
        "save": "Guardar",
        "delete": "Eliminar",
        "edit": "Editar",
        "language": "Idioma",
        "theme": "Tema",
        "light": "Claro",
        "dark": "Oscuro",
        "no_transactions": "No se encontraron transacciones.",
        "date": "Fecha",
        "price": "Precio (€)",
        "actions": "Acciones"
    }
}

# Session state
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

def get_translation(key):
    return str(LANGUAGES[st.session_state.language].get(key, key))

def get_scalar(val):
    if isinstance(val, (pd.Series, list, tuple)):
        return val[0]
    return val

# Database setup
DB = 'finance_tracker.db'
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_name TEXT,
        buy_date TEXT,
        buy_price REAL,
        sell_date TEXT,
        sell_price REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_name TEXT,
        date TEXT,
        price REAL
    )''')
    conn.commit()
    conn.close()
init_db()

# Add sample data if empty
def add_sample_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM transactions")
    if c.fetchone()[0] == 0:
        # Sample transactions (early 90s and recent)
        txs = [
            ("SP500", "1990-01-02", 353.4, None, None),  # Benchmark, never sold
            ("AAPL", "1992-12-15", 0.30, "2000-01-10", 25.0),
            ("IBM", "1991-06-10", 20.0, "2001-08-20", 60.0),
            ("GOOG", "2004-08-19", 85.0, "2014-08-19", 600.0),
            ("MSFT", "1993-03-13", 21.0, "2000-01-10", 39.0),
            ("TSLA", "2010-06-29", 17.0, "2020-06-29", 1000.0),
            ("VOO", "2011-09-09", 100.0, None, None),
            ("EEM", "2003-04-14", 25.0, None, None),
            ("AAPL", "2022-01-10", 140.0, "2023-01-10", 170.0),
            ("TSLA", "2023-02-10", 200.0, "2023-03-01", 220.0)
        ]
        for t in txs:
            c.execute("INSERT INTO transactions (stock_name, buy_date, buy_price, sell_date, sell_price) VALUES (?, ?, ?, ?, ?)", t)
        # Sample price history (SP500 and others)
        prices = [
            ("SP500", "1990-01-02", 353.4), ("SP500", "2000-01-03", 1455.2), ("SP500", "2010-01-04", 1132.99), ("SP500", "2020-01-02", 3257.85), ("SP500", "2023-12-29", 4769.83),
            ("AAPL", "1992-12-15", 0.30), ("AAPL", "2000-01-10", 25.0), ("AAPL", "2022-01-10", 140.0), ("AAPL", "2023-01-10", 170.0),
            ("IBM", "1991-06-10", 20.0), ("IBM", "2001-08-20", 60.0),
            ("GOOG", "2004-08-19", 85.0), ("GOOG", "2014-08-19", 600.0),
            ("MSFT", "1993-03-13", 21.0), ("MSFT", "2000-01-10", 39.0),
            ("TSLA", "2010-06-29", 17.0), ("TSLA", "2020-06-29", 1000.0), ("TSLA", "2023-02-10", 200.0), ("TSLA", "2023-03-01", 220.0),
            ("VOO", "2011-09-09", 100.0), ("VOO", "2023-12-31", 420.0),
            ("EEM", "2003-04-14", 25.0), ("EEM", "2023-12-31", 38.0)
        ]
        for p in prices:
            c.execute("INSERT INTO prices (stock_name, date, price) VALUES (?, ?, ?)", p)
        conn.commit()
    conn.close()
add_sample_data()

# Sidebar
with st.sidebar:
    st.title("💶 " + get_translation("title"))
    language = st.selectbox(get_translation("language"), ["English", "Spanish"], index=0 if st.session_state.language=="English" else 1)
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()
    theme = st.selectbox(get_translation("theme"), [get_translation("light"), get_translation("dark")], index=0 if st.session_state.theme=="light" else 1)
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()
    selected = option_menu(
        menu_title=None,
        options=[get_translation("dashboard"), get_translation("transactions")],
        icons=["bar-chart", "list-task"],
        default_index=0,
    )

# Theme CSS
st.markdown("""
<style>
    .main {padding: 2rem;}
    .stMetric {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;}
    @media (max-width: 768px) {.main {padding: 1rem;}}
    .stButton > button {border-radius: 10px; font-weight: bold;}
    .stSelectbox > div > div {border-radius: 8px;}
    .stTextInput > div > div > input {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)
if st.session_state.theme == get_translation("dark"):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {background-color: #2d3748 !important;}
        .stApp {background-color: #1a202c !important; color: #e2e8f0 !important;}
        .stMarkdown, .stText {color: #e2e8f0 !important;}
        .stMetric {background-color: #2d3748 !important; color: #e2e8f0 !important;}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {background-color: #f0f2f6 !important;}
        .stApp {background-color: #ffffff !important; color: #262730 !important;}
        .stMarkdown, .stText {color: #262730 !important;}
        .stMetric {background-color: #f0f2f6 !important; color: #262730 !important;}
    </style>
    """, unsafe_allow_html=True)

# --- Dashboard ---
if selected == get_translation("dashboard"):
    st.header("📈 " + get_translation("dashboard"))
    conn = sqlite3.connect(DB)
    prices_df = pd.read_sql_query("SELECT * FROM prices", conn)
    tx_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    # Format dates for display
    prices_df['date'] = pd.to_datetime(prices_df['date']).dt.strftime('%d/%m/%Y')
    tx_df['buy_date'] = pd.to_datetime(tx_df['buy_date']).dt.strftime('%d/%m/%Y')
    tx_df['sell_date'] = tx_df['sell_date'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notnull(x) else None)
    # Graph
    if not prices_df.empty:
        # Exclude SP500 from the price evolution chart
        prices_no_sp500 = prices_df[prices_df['stock_name'] != 'SP500']
        if not prices_no_sp500.empty:
            fig = px.line(prices_no_sp500, x="date", y="price", color="stock_name", markers=True, title="Stock/ETF Price Evolution")
            st.plotly_chart(fig, use_container_width=True)
    # --- Percentage Variation Chart (with SP500 benchmark) ---
    st.subheader("% Variation vs. Initial Price (Benchmark: S&P 500)")
    # Prepare data for percentage variation
    pct_df = prices_df.copy()
    pct_df['price'] = pct_df['price'].astype(float)
    pct_df['date'] = pd.to_datetime(pct_df['date'], dayfirst=True)
    pct_df = pct_df.sort_values(['stock_name', 'date'])
    pct_df['pct_var'] = 0.0
    for stock in pct_df['stock_name'].unique():
        stock_mask = pct_df['stock_name'] == stock
        stock_prices = pct_df.loc[stock_mask, 'price']
        initial_price = stock_prices.iloc[0]
        pct_df.loc[stock_mask, 'pct_var'] = (stock_prices / initial_price - 1) * 100
    # Only plot stocks with at least 2 data points
    stocks_to_plot = [s for s in pct_df['stock_name'].unique() if (pct_df[pct_df['stock_name'] == s].shape[0] > 1)]
    fig_pct = px.line(
        pct_df[pct_df['stock_name'].isin(stocks_to_plot)],
        x="date", y="pct_var", color="stock_name", markers=True,
        title="% Variation from Initial Price (S&P 500 as Benchmark)",
        labels={"pct_var": "% Variation", "date": "Date", "stock_name": "Stock/ETF"}
    )
    st.plotly_chart(fig_pct, use_container_width=True)
    # Current holdings
    st.subheader(get_translation("owned"))
    current = tx_df[tx_df['sell_date'].isnull()]
    if not current.empty:
        conn = sqlite3.connect(DB)
        price_map = {}
        for stock in current['stock_name']:
            last_price = pd.read_sql_query(
                "SELECT price FROM prices WHERE stock_name=? ORDER BY date DESC LIMIT 1",
                conn,
                params=[stock]
            )
            price_map[stock] = last_price['price'].iloc[0] if not last_price.empty else None
        conn.close()
        data = []
        for _, row in current.iterrows():
            stock = row['stock_name']
            buy_price = row['buy_price']
            buy_date = row['buy_date']
            current_price = price_map.get(stock, None)
            pct = None
            if current_price is not None:
                try:
                    pct = float((current_price - buy_price) / buy_price * 100)
                except Exception:
                    pct = None
            data.append({
                get_translation("stock_name"): stock,
                get_translation("buy_date"): buy_date,
                get_translation("buy_price"): buy_price,
                get_translation("current_price"): current_price,
                get_translation("variation"): f"{pct:.2f}%" if pct is not None else "-"
            })
        df_current = pd.DataFrame(data)
        if not df_current.empty:
            st.dataframe(df_current)
        else:
            st.info(get_translation("no_transactions"))
    else:
        st.info(get_translation("no_transactions"))
    # Past holdings
    st.subheader(get_translation("history"))
    past = tx_df[tx_df['sell_date'].notnull()]
    data = []
    for _, row in past.iterrows():
        stock = row['stock_name']
        buy_price = row['buy_price']
        buy_date = get_scalar(row['buy_date'])
        sell_price = get_scalar(row['sell_price'])
        buy_date_disp = str(buy_date) if buy_date is not None else "-"
        if sell_price is not None:
            sell_price_scalar = float(sell_price)
        else:
            sell_price_scalar = None
        gain_loss = (sell_price_scalar - buy_price) if sell_price_scalar is not None else None
        pct = ((sell_price_scalar - buy_price) / buy_price * 100) if sell_price_scalar is not None else None
        color = "#008000" if gain_loss is not None and gain_loss > 0 else "#ff0000"
        data.append({
            get_translation("stock_name"): stock,
            get_translation("buy_date"): buy_date_disp,
            get_translation("buy_price"): buy_price,
            get_translation("sell_price"): sell_price_scalar if sell_price_scalar is not None else "-",
            get_translation("variation"): f"{pct:.2f}%" if pct is not None else "-"
        })
    df_past = pd.DataFrame(data)
    if not df_past.empty:
        st.dataframe(df_past)
    else:
        st.info(get_translation("no_transactions"))

# --- Transactions ---
if selected == get_translation("transactions"):
    st.header("📝 " + get_translation("transactions"))
    # Add transaction form
    with st.form("add_tx_form"):
        col1, col2 = st.columns(2)
        with col1:
            stock_name = st.text_input(get_translation("stock_name"))
            buy_date = st.date_input(get_translation("buy_date"), value=datetime.now().date())
            buy_price = st.number_input(get_translation("buy_price"), min_value=0.0, value=100.0, step=0.01)
        with col2:
            sell_date = st.date_input(get_translation("sell_date"), value=datetime.now().date())
            sell_price = st.number_input(get_translation("sell_price"), min_value=0.0, value=0.0, step=0.01)
        submitted = st.form_submit_button(get_translation("save"))
        if submitted and stock_name:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            # Insert transaction
            c.execute("INSERT INTO transactions (stock_name, buy_date, buy_price, sell_date, sell_price) VALUES (?, ?, ?, ?, ?)",
                      (stock_name, buy_date.strftime('%Y-%m-%d'), buy_price, sell_date.strftime('%Y-%m-%d') if sell_price > 0 else None, sell_price if sell_price > 0 else None))
            # Add price history for buy and sell
            c.execute("INSERT INTO prices (stock_name, date, price) VALUES (?, ?, ?)", (stock_name, buy_date.strftime('%Y-%m-%d'), buy_price))
            if sell_price > 0:
                c.execute("INSERT INTO prices (stock_name, date, price) VALUES (?, ?, ?)", (stock_name, sell_date.strftime('%Y-%m-%d'), sell_price))
            conn.commit()
            conn.close()
            st.success("Transaction saved!")
    # Transaction history
    st.subheader(get_translation("history"))
    conn = sqlite3.connect(DB)
    tx_df = pd.read_sql_query("SELECT * FROM transactions ORDER BY buy_date DESC", conn)
    conn.close()
    # Format dates for display
    tx_df['buy_date'] = pd.to_datetime(tx_df['buy_date']).dt.strftime('%d/%m/%Y')
    tx_df['sell_date'] = tx_df['sell_date'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notnull(x) else None)
    if not tx_df.empty:
        data = []
        delete_ids = []
        for idx, row in tx_df.iterrows():
            buy_price = row['buy_price']
            sell_price = get_scalar(row['sell_price'])
            sell_date = get_scalar(row['sell_date'])
            buy_date = get_scalar(row['buy_date'])
            if sell_price is not None:
                sell_price_scalar = float(sell_price)
            else:
                sell_price_scalar = None
            if sell_date is not None:
                sell_date_scalar = str(sell_date)
            else:
                sell_date_scalar = "-"
            if buy_date is not None:
                buy_date_disp = str(buy_date)
            else:
                buy_date_disp = "-"
            gain_loss = (sell_price_scalar - buy_price) if sell_price_scalar is not None else None
            pct = ((sell_price_scalar - buy_price) / buy_price * 100) if sell_price_scalar is not None else None
            color = "#008000" if gain_loss is not None and gain_loss > 0 else "#ff0000"
            delete_button = st.button(f"Delete {row['stock_name']} {buy_date_disp}", key=f"delete_{row['id']}")
            if delete_button:
                # Delete from DB
                conn = sqlite3.connect(DB)
                c = conn.cursor()
                # Remove from transactions
                c.execute("DELETE FROM transactions WHERE id=?", (row['id'],))
                # Remove from prices (by stock and buy/sell date)
                c.execute("DELETE FROM prices WHERE stock_name=? AND date=?", (row['stock_name'], datetime.strptime(buy_date_disp, '%d/%m/%Y').strftime('%Y-%m-%d')))
                if sell_date_scalar != "-":
                    c.execute("DELETE FROM prices WHERE stock_name=? AND date=?", (row['stock_name'], datetime.strptime(sell_date_scalar, '%d/%m/%Y').strftime('%Y-%m-%d')))
                conn.commit()
                conn.close()
                st.rerun()
            data.append({
                get_translation("stock_name"): row['stock_name'],
                get_translation("buy_date"): buy_date_disp,
                get_translation("buy_price"): buy_price,
                get_translation("sell_date"): sell_date_scalar,
                get_translation("sell_price"): sell_price_scalar if sell_price_scalar is not None else "-",
                get_translation("gain_loss"): f"<span style='color:{color}'>{gain_loss:.2f}</span>" if gain_loss is not None else "-",
                get_translation("gain_loss_pct"): f"<span style='color:{color}'>{pct:.2f}%</span>" if pct is not None else "-"
            })
        st.write(pd.DataFrame(data).to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info(get_translation("no_transactions")) 