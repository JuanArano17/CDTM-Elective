import streamlit as st
import json
import os
from collections import defaultdict

# --- File paths for persistent storage ---
GROCERIES_FILE = 'groceries.json'
CATEGORIES_FILE = 'categories.json'

# --- Default data ---
DEFAULT_CATEGORIES = ["Produce", "Dairy", "Bakery", "Meat", "Frozen", "Pantry", "Beverages", "Household"]
DEFAULT_GROCERIES = [
    {"name": "Apple", "unit": "count", "category": "Produce"},
    {"name": "Milk", "unit": "l", "category": "Dairy"},
    {"name": "Bread", "unit": "count", "category": "Bakery"},
    {"name": "Chicken Breast", "unit": "g", "category": "Meat"},
    {"name": "Eggs", "unit": "count", "category": "Dairy"},
    {"name": "Rice", "unit": "kg", "category": "Pantry"},
    {"name": "Orange Juice", "unit": "l", "category": "Beverages"},
]

# --- Helper functions for persistent storage ---
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# --- Load or initialize groceries and categories ---
def get_groceries():
    groceries = load_json(GROCERIES_FILE, DEFAULT_GROCERIES)
    return groceries

def get_categories():
    categories = load_json(CATEGORIES_FILE, DEFAULT_CATEGORIES)
    return categories

def save_groceries(groceries):
    save_json(GROCERIES_FILE, groceries)

def save_categories(categories):
    save_json(CATEGORIES_FILE, categories)

# --- Session state initialization ---
if 'grocery_lists' not in st.session_state:
    st.session_state['grocery_lists'] = {}
if 'current_list' not in st.session_state:
    st.session_state['current_list'] = None
if 'groceries' not in st.session_state:
    st.session_state['groceries'] = get_groceries()
if 'categories' not in st.session_state:
    st.session_state['categories'] = get_categories()

# --- Sidebar: List management ---
st.sidebar.title("Grocery Lists")
list_names = list(st.session_state['grocery_lists'].keys())
selected_list = st.sidebar.selectbox("Select a list", [None] + list_names, index=0, key="list_select")

if selected_list:
    st.session_state['current_list'] = selected_list
else:
    st.session_state['current_list'] = None

new_list_name = st.sidebar.text_input("New list name", key="new_list_name")
if st.sidebar.button("Create List") and new_list_name:
    if new_list_name not in st.session_state['grocery_lists']:
        st.session_state['grocery_lists'][new_list_name] = []
        st.session_state['current_list'] = new_list_name
        st.sidebar.success(f"Created list '{new_list_name}'!")
    else:
        st.sidebar.warning("List already exists.")

if st.session_state['current_list']:
    if st.sidebar.button("Delete List"):
        del st.session_state['grocery_lists'][st.session_state['current_list']]
        st.session_state['current_list'] = None
        st.experimental_rerun()

# --- Main: Add groceries to list ---
st.title("Grocery List Planner")

if st.session_state['current_list']:
    st.header(f"List: {st.session_state['current_list']}")
    groceries = st.session_state['groceries']
    categories = st.session_state['categories']
    grocery_names = [g['name'] for g in groceries]
    grocery_name = st.selectbox("Grocery", grocery_names + ["Add new grocery..."])
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0, value=1.0)
    unit = st.selectbox("Unit", ["count", "g", "kg", "ml", "l"])

    if grocery_name == "Add new grocery...":
        with st.form("add_grocery_form", clear_on_submit=True):
            new_grocery_name = st.text_input("Grocery name")
            new_grocery_unit = st.selectbox("Default unit", ["count", "g", "kg", "ml", "l"], key="new_grocery_unit")
            new_grocery_category = st.selectbox("Category", categories + ["Add new category..."])
            if new_grocery_category == "Add new category...":
                new_category = st.text_input("New category name")
            else:
                new_category = None
            submitted = st.form_submit_button("Add Grocery")
            if submitted and new_grocery_name:
                if new_grocery_category == "Add new category..." and new_category:
                    categories.append(new_category)
                    save_categories(categories)
                    st.session_state['categories'] = categories
                    chosen_category = new_category
                else:
                    chosen_category = new_grocery_category
                new_grocery = {"name": new_grocery_name, "unit": new_grocery_unit, "category": chosen_category}
                groceries.append(new_grocery)
                save_groceries(groceries)
                st.session_state['groceries'] = groceries
                st.success(f"Added new grocery: {new_grocery_name}")
                st.experimental_rerun()
    else:
        if st.button("Add to List"):
            # Add or update item in the list
            current_list = st.session_state['grocery_lists'][st.session_state['current_list']]
            found = False
            for item in current_list:
                if item['name'] == grocery_name and item['unit'] == unit:
                    item['quantity'] += quantity
                    found = True
                    break
            if not found:
                grocery = next((g for g in groceries if g['name'] == grocery_name), None)
                category = grocery['category'] if grocery else "Other"
                current_list.append({
                    "name": grocery_name,
                    "quantity": quantity,
                    "unit": unit,
                    "category": category,
                    "checked": False
                })
            st.success(f"Added {quantity} {unit} {grocery_name} to list.")

    # --- Display grouped grocery list ---
    st.subheader("Your List (grouped by area)")
    current_list = st.session_state['grocery_lists'][st.session_state['current_list']]
    grouped = defaultdict(list)
    for item in current_list:
        grouped[item['category']].append(item)

    for category in categories:
        if category in grouped:
            st.markdown(f"**{category}**")
            for idx, item in enumerate(grouped[category]):
                col1, col2, col3, col4 = st.columns([4,2,2,1])
                with col1:
                    st.write(f"{item['name']}")
                with col2:
                    st.write(f"{item['quantity']} {item['unit']}")
                with col3:
                    checked = st.checkbox("Checked", value=item['checked'], key=f"{item['name']}_{idx}")
                    item['checked'] = checked
                with col4:
                    if st.button("Remove", key=f"remove_{item['name']}_{idx}"):
                        current_list.remove(item)
                        st.experimental_rerun()

    # Save changes to session state
    st.session_state['grocery_lists'][st.session_state['current_list']] = current_list
else:
    st.info("Create or select a grocery list to get started.")
