import streamlit as st
from datetime import datetime
from collections import defaultdict
from pint import UnitRegistry
ureg = UnitRegistry()
import requests
import random
import pyttsx3
import pandas as pd
import os

LISTS_CSV = os.path.join(os.path.dirname(__file__), 'grocery_lists.csv')

st.set_page_config(page_title="Groli - Grocery List Manager", layout="wide")

# --- Persistence Functions ---
def save_lists_to_csv(lists):
    rows = []
    for list_id, list_obj in lists.items():
        for item in list_obj["items"]:
            rows.append({
                "list_id": list_id,
                "list_name": list_obj["name"],
                "last_edited": list_obj["last_edited"],
                "item_name": item["name"],
                "area": item["area"],
                "quantity": item["quantity"],
                "unit": item["unit"],
                "checked": item["checked"],
            })
        if not list_obj["items"]:
            # Save empty lists too
            rows.append({
                "list_id": list_id,
                "list_name": list_obj["name"],
                "last_edited": list_obj["last_edited"],
                "item_name": "",
                "area": "",
                "quantity": "",
                "unit": "",
                "checked": "",
            })
    df = pd.DataFrame(rows)
    df.to_csv(LISTS_CSV, index=False)

def load_lists_from_csv():
    if not os.path.exists(LISTS_CSV) or os.path.getsize(LISTS_CSV) == 0:
        return {}
    try:
        df = pd.read_csv(LISTS_CSV)
    except pd.errors.EmptyDataError:
        return {}
    lists = {}
    for _, row in df.iterrows():
        list_id = str(row["list_id"])
        if list_id not in lists:
            # Parse last_edited as datetime if possible
            last_edited = row["last_edited"] if not pd.isna(row["last_edited"]) else None
            try:
                if last_edited:
                    last_edited = pd.to_datetime(last_edited)
            except Exception:
                pass
            lists[list_id] = {
                "name": row["list_name"],
                "items": [],
                "last_edited": last_edited,
            }
        if pd.notna(row["item_name"]) and row["item_name"]:
            lists[list_id]["items"].append({
                "name": row["item_name"],
                "area": row["area"],
                "quantity": float(row["quantity"]),
                "unit": row["unit"],
                "checked": bool(row["checked"]),
            })
    return lists

# --- Load lists on app start ---
if "grocery_lists" not in st.session_state:
    st.session_state.grocery_lists = load_lists_from_csv()

# --- Save lists on any change ---
def get_lists():
    if "grocery_lists" not in st.session_state:
        st.session_state.grocery_lists = {}
    return st.session_state.grocery_lists

def save_and_rerun():
    save_lists_to_csv(st.session_state.grocery_lists)
    st.rerun()

# --- Helper Functions ---
def get_last_edited(list_obj):
    le = list_obj.get("last_edited", datetime.min)
    if isinstance(le, str):
        try:
            le = pd.to_datetime(le)
        except Exception:
            le = datetime.min
    return le

def update_last_edited(list_id):
    lists = get_lists()
    if list_id in lists:
        lists[list_id]["last_edited"] = datetime.now()

# --- Sidebar ---
st.sidebar.title("Groli")

# New list creation
with st.sidebar.form(key="create_list_sidebar_form", clear_on_submit=True):
    new_list_name = st.text_input("New List Name", key="sidebar_new_list_name")
    create_list_btn = st.form_submit_button("Create New List")
    if create_list_btn and new_list_name.strip():
        lists = get_lists()
        list_id = str(datetime.now().timestamp())
        lists[list_id] = {
            "name": new_list_name.strip(),
            "items": [],
            "last_edited": datetime.now(),
        }
        st.session_state.selected_list = list_id
        save_and_rerun()

# List selection
lists = get_lists()
ordered_lists = sorted(lists.items(), key=lambda x: get_last_edited(x[1]), reverse=True)

st.sidebar.markdown("### Your Lists")
for list_id, list_obj in ordered_lists:
    if st.sidebar.button(list_obj["name"], key=f"sidebar_select_{list_id}"):
        st.session_state.selected_list = list_id

# --- Main Area ---
if "selected_list" not in st.session_state:
    st.title("Welcome to Groli!")
    st.write("Create and manage grocery lists grouped by store areas.")
else:
    # --- List View UI ---
    selected_list_id = st.session_state.selected_list
    lists = get_lists()
    if selected_list_id not in lists:
        st.error("Selected list not found.")
    else:
        grocery_list = lists[selected_list_id]
        # --- Price Estimation ---
        def fetch_price(item_name, quantity, unit):
            # Example API endpoint (replace with real one if available)
            api_url = f"https://api.example.com/grocery_price?item={item_name}&unit={unit}"
            try:
                response = requests.get(api_url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    # Assume API returns price per unit
                    price_per_unit = data.get("price_per_unit", None)
                    if price_per_unit is not None:
                        return price_per_unit * quantity
            except Exception:
                pass
            # Fallback: random price for demo
            return round(random.uniform(0.5, 3.0) * quantity, 2)

        estimated_total = 0.0
        price_details = []
        for item in grocery_list["items"]:
            if not item["checked"]:
                price = fetch_price(item["name"], item["quantity"], item["unit"])
                estimated_total += price
                price_details.append((item["name"], price))

        # --- Editable List Name ---
        col1, col2, col3 = st.columns([6,1,1])
        with col1:
            if st.session_state.get(f"edit_name_{selected_list_id}", False):
                new_name = st.text_input("Edit List Name", value=grocery_list["name"], key=f"edit_name_input_{selected_list_id}")
                save, cancel = st.columns([1,1])
                with save:
                    if st.button("💾 Save", key=f"save_name_{selected_list_id}"):
                        grocery_list["name"] = new_name.strip() or grocery_list["name"]
                        update_last_edited(selected_list_id)
                        st.session_state[f"edit_name_{selected_list_id}"] = False
                        save_and_rerun()
                with cancel:
                    if st.button("❌ Cancel", key=f"cancel_name_{selected_list_id}"):
                        st.session_state[f"edit_name_{selected_list_id}"] = False
                        save_and_rerun()
            else:
                st.markdown(f"## {grocery_list['name']}")
                st.markdown(f"**Estimated: ${estimated_total:.2f}**")
                with st.expander("Show price breakdown"):
                    for name, price in price_details:
                        st.write(f"{name}: ${price:.2f}")
                # --- Accessibility: Read Out List ---
                def get_list_text():
                    if not grocery_list["items"]:
                        return "Your grocery list is empty."
                    lines = []
                    for item in grocery_list["items"]:
                        if not item["checked"]:
                            lines.append(f"{item['quantity']} {item['unit']} of {item['name']} in {item['area']}")
                    if not lines:
                        return "All items are checked off."
                    return "You need to buy: " + ", ".join(lines) + "."
                if st.button("🔊 Read Out List", key=f"readout_{selected_list_id}"):
                    engine = pyttsx3.init()
                    engine.say(get_list_text())
                    engine.runAndWait()
        with col2:
            if st.button("✏️", key=f"edit_btn_{selected_list_id}"):
                st.session_state[f"edit_name_{selected_list_id}"] = True
                save_and_rerun()
        with col3:
            if st.button("🗑️ Delete List", key=f"delete_list_{selected_list_id}"):
                del lists[selected_list_id]
                st.session_state.pop("selected_list")
                save_and_rerun()

        st.markdown("---")
        # --- Add Item Form ---
        with st.form(key=f"add_item_form_{selected_list_id}", clear_on_submit=True):
            c1, c2, c3, c4, c5 = st.columns([3,3,2,2,2])
            with c1:
                item_name = st.text_input("Grocery", key=f"item_name_{selected_list_id}")
            with c2:
                area = st.text_input("Area", key=f"area_{selected_list_id}")
            with c3:
                quantity = st.number_input("Quantity", min_value=1, value=1, key=f"quantity_{selected_list_id}")
            with c4:
                unit = st.selectbox("Unit", ["pieces", "kg", "g", "l", "ml"], key=f"unit_{selected_list_id}")
            with c5:
                st.write("")
                add_item_btn = st.form_submit_button("Add Item")
            if add_item_btn and item_name.strip() and area.strip():
                # Always convert to base units before adding/merging
                def get_pint_unit(unit):
                    if unit == "kg": return ureg.kilogram
                    if unit == "g": return ureg.gram
                    if unit == "l": return ureg.liter
                    if unit == "ml": return ureg.milliliter
                    return None
                base_unit = unit
                base_qty = quantity
                if unit == "ml":
                    base_qty = (quantity * ureg.milliliter).to("liter").magnitude
                    base_unit = "l"
                elif unit == "g":
                    base_qty = (quantity * ureg.gram).to("kilogram").magnitude
                    base_unit = "kg"
                # Try to merge with compatible units
                found = False
                for item in grocery_list["items"]:
                    if (
                        item["name"].lower() == item_name.strip().lower()
                        and item["area"].lower() == area.strip().lower()
                    ):
                        # Check if units are compatible
                        item_pint_unit = get_pint_unit(item["unit"])
                        new_pint_unit = get_pint_unit(base_unit)
                        if item_pint_unit and new_pint_unit and base_unit in ["kg", "l"]:
                            # Convert both to base unit
                            item_qty = (item["quantity"] * item_pint_unit).to(base_unit).magnitude
                            new_qty = base_qty
                            item["quantity"] = item_qty + new_qty
                            item["unit"] = base_unit
                            found = True
                            break
                        elif item["unit"] == base_unit:
                            item["quantity"] += base_qty
                            found = True
                            break
                if not found:
                    grocery_list["items"].append({
                        "name": item_name.strip(),
                        "area": area.strip(),
                        "quantity": base_qty,
                        "unit": base_unit,
                        "checked": False,
                    })
                update_last_edited(selected_list_id)
                save_and_rerun()
        # --- Display Items by Area ---
        items_by_area = defaultdict(list)
        for idx, item in enumerate(grocery_list["items"]):
            items_by_area[item["area"]].append((idx, item))
        has_items = len(grocery_list["items"]) > 0
        for area in sorted(items_by_area.keys()):
            st.markdown(f"### {area}")
            # Unchecked first, then checked
            area_items = items_by_area[area]
            unchecked = [x for x in area_items if not x[1]["checked"]]
            checked = [x for x in area_items if x[1]["checked"]]
            for group in [unchecked, checked]:
                for idx, item in group:
                    cbox, namecol, delcol = st.columns([1,6,1])
                    with cbox:
                        checked = st.checkbox("", value=item["checked"], key=f"check_{selected_list_id}_{idx}")
                        if checked != item["checked"]:
                            grocery_list["items"][idx]["checked"] = checked
                            update_last_edited(selected_list_id)
                            save_and_rerun()
                    with namecol:
                        # Format quantity for display
                        qty_disp = item["quantity"]
                        if item["unit"] in ["kg", "l"]:
                            qty_disp = round(qty_disp, 3)
                        st.write(f"{item['name']} ({qty_disp} {item['unit']})")
                    with delcol:
                        if st.button("🗑️", key=f"delete_item_{selected_list_id}_{idx}"):
                            grocery_list["items"].pop(idx)
                            update_last_edited(selected_list_id)
                            save_and_rerun()
        # Only show separator if there are items
        if has_items:
            st.markdown("---")
        # --- Area Overview Chart ---
        import plotly.express as px
        area_totals = {}
        for item in grocery_list["items"]:
            area = item["area"]
            if not item["checked"]:
                qty = item["quantity"]
                unit = item["unit"]
                # Convert to base units for chart
                if unit == "ml":
                    qty = (qty * ureg.milliliter).to("liter").magnitude
                    unit = "l"
                elif unit == "g":
                    qty = (qty * ureg.gram).to("kilogram").magnitude
                    unit = "kg"
                # For pieces, kg, l, just use as is
                area_totals.setdefault(area, 0)
                area_totals[area] += qty
        if area_totals:
            import plotly.express as px
            fig = px.bar(
                x=list(area_totals.keys()),
                y=list(area_totals.values()),
                labels={'x': 'Area', 'y': 'Total Quantity (base units)'},
                color=list(area_totals.keys()),
            )
            st.markdown("### Overview: Total Quantity per Area")
            st.markdown("*Helps you plan your route through the store by showing where most of your shopping is concentrated.*")
            st.plotly_chart(fig, use_container_width=True)