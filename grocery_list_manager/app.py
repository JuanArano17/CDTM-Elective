import streamlit as st
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="Groli - Grocery List Manager", layout="wide")

# --- Helper Functions ---
def get_lists():
    if "grocery_lists" not in st.session_state:
        st.session_state.grocery_lists = {}
    return st.session_state.grocery_lists

def get_last_edited(list_obj):
    return list_obj.get("last_edited", datetime.min)

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
                with cancel:
                    if st.button("❌ Cancel", key=f"cancel_name_{selected_list_id}"):
                        st.session_state[f"edit_name_{selected_list_id}"] = False
            else:
                st.markdown(f"## {grocery_list['name']}")
        with col2:
            if st.button("✏️", key=f"edit_btn_{selected_list_id}"):
                st.session_state[f"edit_name_{selected_list_id}"] = True
        with col3:
            if st.button("🗑️ Delete List", key=f"delete_list_{selected_list_id}"):
                del lists[selected_list_id]
                st.session_state.pop("selected_list")
                st.experimental_rerun()

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
                # Merge logic
                found = False
                for item in grocery_list["items"]:
                    if (
                        item["name"].lower() == item_name.strip().lower()
                        and item["area"].lower() == area.strip().lower()
                        and item["unit"] == unit
                    ):
                        item["quantity"] += quantity
                        found = True
                        break
                if not found:
                    grocery_list["items"].append({
                        "name": item_name.strip(),
                        "area": area.strip(),
                        "quantity": quantity,
                        "unit": unit,
                        "checked": False,
                    })
                update_last_edited(selected_list_id)
                st.experimental_rerun()

        # --- Display Items by Area ---
        items_by_area = defaultdict(list)
        for idx, item in enumerate(grocery_list["items"]):
            items_by_area[item["area"]].append((idx, item))
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
                            st.experimental_rerun()
                    with namecol:
                        st.write(f"{item['name']} ({item['quantity']} {item['unit']})")
                    with delcol:
                        if st.button("🗑️", key=f"delete_item_{selected_list_id}_{idx}"):
                            grocery_list["items"].pop(idx)
                            update_last_edited(selected_list_id)
                            st.experimental_rerun() 