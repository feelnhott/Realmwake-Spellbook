import json
import streamlit as st

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Realmwake Spellbook", page_icon="📜", layout="wide"
)

# Centered and enlarged title using HTML/CSS styling
st.markdown(
    "<h1 style='text-align: center; font-size: 3.5rem;'>📜 Realmwake"
    " Spellbook</h1>",
    unsafe_allow_html=True,
)

# --- DEFAULT TEMPLATE DATA ---
DEFAULT_DATA = {
    "characters": ["Default Caster"],
    "mana": {"Default Caster": {"max": 50, "current": 50}},
    "stats": {
        "Default Caster": {
            "max_prepared": 5,
            "spell_attack": 3,
            "spell_dc": 13,
        }
    },
    "spells": [
        {
            "name": "Arcane Missile",
            "character": "Default Caster",
            "level": 1,
            "school": "Evocation",
            "domain": "Arcane",
            "casting_time": "A",
            "duration": "Instantaneous",
            "range": "120 feet",
            "ritual": "No",
            "components": "V, S",
            "description": "Fires energy darts at targets.",
            "prepared": True,
        }
    ],
}

# --- INITIALIZE SESSION STATE ---
if "spellbook_data" not in st.session_state:
    st.session_state["spellbook_data"] = DEFAULT_DATA


def save_data(data):
    """Saves data into session state to ensure instant UI updates."""
    st.session_state["spellbook_data"] = data


# --- SIDEBAR: CLOUD DATA MANAGEMENT (IMPORT / EXPORT) ---
st.sidebar.header("💾 Data Management")
with st.sidebar.expander("📁 Import Spellbook", expanded=False):
    uploaded_file = st.file_uploader(
        "Upload your spells_data.json", type=["json"]
    )

    # If a file is uploaded, parse it once and load it into session state safely
    if uploaded_file is not None:
        file_id = getattr(uploaded_file, "file_id", uploaded_file.name)
        if st.session_state.get("processed_file_id") != file_id:
            try:
                content = json.load(uploaded_file)
                if "mana" not in content:
                    content["mana"] = {}
                if "stats" not in content:
                    content["stats"] = {}
                st.session_state["spellbook_data"] = content
                st.session_state["processed_file_id"] = file_id
                st.sidebar.success("Successfully loaded spellbook!")
            except Exception as e:
                st.sidebar.error(f"Error reading uploaded JSON file: {e}")

    st.markdown("---")
    st.markdown(
        "*Tip: Download your JSON file before leaving to save your progress!*"
    )

# Pull current active data from session state
data = st.session_state["spellbook_data"]

# Provide a download button for the current JSON state in the sidebar
json_str = json.dumps(data, indent=4)
st.sidebar.download_button(
    label="📥 Download spells_data.json",
    data=json_str,
    file_name="spells_data.json",
    mime="application/json",
    use_container_width=True,
)

st.sidebar.markdown("---")


# --- SIDEBAR: CHARACTER MANAGEMENT ---
character_list = data.get("characters", ["Default Caster"])
if not character_list:
    data["characters"] = ["Default Caster"]
    character_list = ["Default Caster"]

selected_character = st.sidebar.selectbox(
    "Active Character Profile:", character_list
)

# Ensure active character has mana entries
if selected_character not in data["mana"]:
    data["mana"][selected_character] = {"max": 50, "current": 50}
    save_data(data)

# Ensure active character has stats entries
if "stats" not in data:
    data["stats"] = {}
if selected_character not in data["stats"]:
    data["stats"][selected_character] = {
        "max_prepared": 5,
        "spell_attack": 3,
        "spell_dc": 13,
    }
    save_data(data)

# Initialize expander state session variable if not present
if "manage_char_expander" not in st.session_state:
    st.session_state["manage_char_expander"] = False

# Collapsible Expander for Character Management with state control key
with st.sidebar.expander(
    "🧙 Manage Character Profiles", key="manage_char_expander"
):
    # Add New Character Form
    st.markdown("### ➕ Create New Character")
    new_char_name = st.text_input("Character Name", key="input_new_char_name")
    if st.button("Add Character") and new_char_name:
        if new_char_name not in data["characters"]:
            data["characters"].append(new_char_name)
            data["mana"][new_char_name] = {"max": 50, "current": 50}
            data["stats"][new_char_name] = {
                "max_prepared": 5,
                "spell_attack": 3,
                "spell_dc": 13,
            }
            save_data(data)
            st.session_state["manage_char_expander"] = False
            st.success(f"Added {new_char_name}!")
            st.rerun()

    st.markdown("---")

    # Delete Active Character
    st.markdown("### 🗑️ Delete Current Character")
    st.warning(f"Delete **{selected_character}** and all associated spells?")
    confirm_del = st.checkbox("Yes, I understand", key="confirm_delete_char")
    if st.button("Delete Character", disabled=not confirm_del):
        data["characters"].remove(selected_character)

        if selected_character in data["mana"]:
            del data["mana"][selected_character]
        if selected_character in data["stats"]:
            del data["stats"][selected_character]

        data["spells"] = [
            s for s in data["spells"] if s.get("character") != selected_character
        ]

        if not data["characters"]:
            data["characters"] = ["Default Caster"]

        save_data(data)
        st.session_state["manage_char_expander"] = False
        st.success(f"Deleted {selected_character}!")
        st.rerun()


# --- SIDEBAR: STATS & MANA CONFIGURATION ---
st.sidebar.markdown("---")

char_mana = data["mana"][selected_character]
char_stats = data["stats"][selected_character]

# Collapsible Expander for Character Stats & Mana Configuration
with st.sidebar.expander("⚙️ Configure Stats & Mana"):
    new_max_mana = st.number_input(
        "Configure Max Mana",
        min_value=0,
        max_value=9999,
        value=char_mana["max"],
        key=f"max_mana_{selected_character}",
    )

    new_max_prep = st.number_input(
        "Max Prepared Spells",
        min_value=0,
        max_value=99,
        value=char_stats.get("max_prepared", 5),
        key=f"max_prep_{selected_character}",
    )

    new_spell_atk = st.number_input(
        "Spell Attack Modifier",
        min_value=-10,
        max_value=99,
        value=char_stats.get("spell_attack", 3),
        key=f"spell_atk_{selected_character}",
    )

    new_spell_dc = st.number_input(
        "Spell Save DC",
        min_value=0,
        max_value=99,
        value=char_stats.get("spell_dc", 13),
        key=f"spell_dc_{selected_character}",
    )

    changes_made = False

    if new_max_mana != char_mana["max"]:
        char_mana["max"] = new_max_mana
        if char_mana["current"] > new_max_mana:
            char_mana["current"] = new_max_mana
        changes_made = True

    if (
        new_max_prep != char_stats.get("max_prepared")
        or new_spell_atk != char_stats.get("spell_attack")
        or new_spell_dc != char_stats.get("spell_dc")
    ):
        char_stats["max_prepared"] = new_max_prep
        char_stats["spell_attack"] = new_spell_atk
        char_stats["spell_dc"] = new_spell_dc
        changes_made = True

    if changes_made:
        save_data(data)
        st.rerun()


# --- SIDEBAR: ADD A NEW SPELL (Collapsible) ---
st.sidebar.markdown("---")
with st.sidebar.expander("✍️ Add New Spell"):
    with st.form("add_spell_form"):
        spell_name = st.text_input("Spell Name")
        spell_level = st.number_input(
            "Level", min_value=0, max_value=12, value=0
        )
        spell_school = st.selectbox(
            "School",
            [
                "Abjuration",
                "Conjuration",
                "Divination",
                "Evocation",
                "Geistcraft",
                "Illusion",
                "Necromancy",
                "Transmutation",
                "Zeitcraft",
            ],
        )
        domain = st.selectbox("Domain", ["Arcane", "Chaos", "Divine", "Nature"])
        casting_time = st.text_input("Casting Time", value="A")
        duration = st.text_input("Duration", value="Instantaneous")
        spell_range = st.text_input("Range", value="60 feet")
        ritual = st.text_input("Ritual", value="No")
        components = st.text_input("Components", value="V, S")
        description = st.text_area("Description")
        is_prepared_default = st.checkbox("Prepared by default?", value=False)

        assign_to_char = st.selectbox(
            "Assign to Character:",
            character_list,
            index=character_list.index(selected_character)
            if selected_character in character_list
            else 0,
        )

        submit = st.form_submit_button("Save Spell to Book")

        if submit and spell_name:
            new_spell = {
                "name": spell_name,
                "character": assign_to_char,
                "level": int(spell_level),
                "school": spell_school,
                "domain": domain,
                "casting_time": casting_time,
                "duration": duration,
                "range": spell_range,
                "ritual": ritual,
                "components": components,
                "description": description,
                "prepared": is_prepared_default,
            }
            data["spells"].append(new_spell)
            save_data(data)
            st.sidebar.success(f"Saved '{spell_name}' to {assign_to_char}!")
            st.rerun()


# --- MAIN SECTION: UNIFIED HEADER (Title, Mana, & Stats) ---
atk_val = char_stats.get("spell_attack", 3)
atk_formatted = f"+{atk_val}" if atk_val >= 0 else str(atk_val)

head_col1, head_col2 = st.columns([1.5, 3.5])

with head_col1:
    st.header(f"📖 {selected_character}'s Spellbook")

with head_col2:
    # Cards reordered: Mana -> Prepared Spells -> Spell Attack -> Spell Save DC
    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; width: 100%;">
            <div style="background-color: #2b303c; padding: 8px 10px; border-radius: 8px; border: 1px solid #444; text-align: center;">
                <div style="font-size: 0.75rem; color: #aaa; font-weight: bold; text-transform: uppercase;">Mana</div>
                <div style="font-size: 1rem; color: #33ccff; font-weight: bold;">{char_mana['current']} / {char_mana['max']}</div>
            </div>
            <div style="background-color: #2b303c; padding: 8px 10px; border-radius: 8px; border: 1px solid #444; text-align: center;">
                <div style="font-size: 0.75rem; color: #aaa; font-weight: bold; text-transform: uppercase;">Prepared Spells</div>
                <div style="font-size: 1rem; color: #5cd65c; font-weight: bold;">{char_stats.get('max_prepared', 5)}</div>
            </div>
            <div style="background-color: #2b303c; padding: 8px 10px; border-radius: 8px; border: 1px solid #444; text-align: center;">
                <div style="font-size: 0.75rem; color: #aaa; font-weight: bold; text-transform: uppercase;">Spell Attack</div>
                <div style="font-size: 1rem; color: #4da6ff; font-weight: bold;">{atk_formatted}</div>
            </div>
            <div style="background-color: #2b303c; padding: 8px 10px; border-radius: 8px; border: 1px solid #444; text-align: center;">
                <div style="font-size: 0.75rem; color: #aaa; font-weight: bold; text-transform: uppercase;">Spell Save DC</div>
                <div style="font-size: 1rem; color: #ff6666; font-weight: bold;">{char_stats.get('spell_dc', 13)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action bar tucked directly under the stats row
    act_c1, act_c2, act_c3 = st.columns([1, 1, 1])
    with act_c1:
        cost_input = st.number_input(
            "Cost",
            min_value=1,
            max_value=999,
            value=5,
            key=f"cost_{selected_character}",
            label_visibility="collapsed",
        )
    with act_c2:
        if st.button("⚡ Cast", key=f"cast_btn_{selected_character}use", use_container_width=True):
            if char_mana["current"] >= cost_input:
                char_mana["current"] -= cost_input
            else:
                char_mana["current"] = 0
            save_data(data)
            st.rerun()
    with act_c3:
        if st.button("🧪 Restore", key=f"reset_btn_{selected_character}full", use_container_width=True):
            char_mana["current"] = min(char_mana["max"], char_mana["current"] + cost_input)
            save_data(data)
            st.rerun()

st.markdown("---")

char_spells = [
    s for s in data["spells"] if s.get("character") == selected_character
]

# Quick search bar always visible
search_query = st.text_input("🔍 Quick Search by Spell Name", "")

# Gather unique dynamic options for all filterable fields
all_schools = sorted(
    list(set(s.get("school", "Evocation") for s in char_spells))
)
all_domains = sorted(
    list(set(s.get("domain", "Arcane") for s in char_spells))
)
all_times = sorted(
    list(set(s.get("casting_time", "A") for s in char_spells))
)
all_durations = sorted(
    list(set(s.get("duration", "Instantaneous") for s in char_spells))
)
all_ranges = sorted(
    list(set(s.get("range", "60 feet") for s in char_spells))
)
all_rituals = sorted(
    list(set(s.get("ritual", "No") for s in char_spells))
)
all_comps = sorted(
    list(set(s.get("components", "V, S") for s in char_spells))
)

# Collapsible Expander for Optional / Advanced Filters
with st.expander("🔍 Advanced Filters & Sorting (Optional)"):
    # Top utility row: Prepared state and Sorting options
    top_col1, top_col2 = st.columns(2)
    with top_col1:
        prep_filter = st.selectbox(
            "Show Spells", ["All Spells", "Prepared Only", "Unprepared Only"]
        )
    with top_col2:
        sort_by = st.selectbox(
            "Sort Spells By", ["Level (Low to High)", "Name (A-Z)"]
        )

    st.markdown("---")

    # Filters layout matching the "Add New Spell" form order:
    # Row 1: Level, School, Domain, Casting Time
    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        level_filter = st.multiselect(
            "Filter by Level",
            options=list(range(0, 13)),
            default=list(range(0, 13)),
        )
    with row1_c2:
        school_filter = st.multiselect(
            "School", options=all_schools, default=all_schools
        )
    with row1_c3:
        domain_filter = st.multiselect(
            "Domain", options=all_domains, default=all_domains
        )
    with row1_c4:
        time_filter = st.multiselect(
            "Casting Time", options=all_times, default=all_times
        )

    # Row 2: Duration, Range, Ritual, Components
    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        duration_filter = st.multiselect(
            "Duration", options=all_durations, default=all_durations
        )
    with row2_c2:
        range_filter = st.multiselect(
            "Range", options=all_ranges, default=all_ranges
        )
    with row2_c3:
        ritual_filter = st.multiselect(
            "Ritual", options=all_rituals, default=all_rituals
        )
    with row2_c4:
        comp_filter = st.multiselect(
            "Components", options=all_comps, default=all_comps
        )

# --- APPLY ALL FILTERS SAFELY ---
filtered_spells = char_spells

if search_query:
    filtered_spells = [
        s for s in filtered_spells if search_query.lower() in s["name"].lower()
    ]

if "level_filter" in locals():
    filtered_spells = [s for s in filtered_spells if s["level"] in level_filter]
if "school_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("school", "Evocation") in school_filter
    ]
if "domain_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("domain", "Arcane") in domain_filter
    ]
if "time_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("casting_time", "A") in time_filter
    ]
if "duration_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("duration", "Instantaneous") in duration_filter
    ]
if "range_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("range", "60 feet") in range_filter
    ]
if "ritual_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("ritual", "No") in ritual_filter
    ]
if "comp_filter" in locals():
    filtered_spells = [
        s for s in filtered_spells if s.get("components", "V, S") in comp_filter
    ]

if "prep_filter" in locals():
    if prep_filter == "Prepared Only":
        filtered_spells = [s for s in filtered_spells if s.get("prepared", False)]
    elif prep_filter == "Unprepared Only":
        filtered_spells = [
            s for s in filtered_spells if not s.get("prepared", False)
        ]

sort_selection = sort_by if "sort_by" in locals() else "Level (Low to High)"
if sort_selection == "Level (Low to High)":
    filtered_spells = sorted(filtered_spells, key=lambda x: x["level"])
elif sort_selection == "Name (A-Z)":
    filtered_spells = sorted(filtered_spells, key=lambda x: x["name"])

# --- DISPLAY SPELLS ---
st.write(f"Showing **{len(filtered_spells)}** spells:")

if not filtered_spells:
    st.info("No spells found matching your current filters or character book.")

for i, spell in enumerate(filtered_spells):
    level_label = (
        "Cantrip" if spell["level"] == 0 else f"Level {spell['level']}"
    )
    spell_domain_val = spell.get("domain", "Arcane")
    prep_status = (
        "🟢 Prepared" if spell.get("prepared", False) else "⚪ Unprepared"
    )

    with st.expander(
        f"**{spell['name']}** — *{level_label} ({spell_domain_val} / {spell['school']})* | {prep_status}"
    ):
        current_prep_state = spell.get("prepared", False)
        new_prep_state = st.checkbox(
            "Prepared for today",
            value=current_prep_state,
            key=f"prop_toggle_{selected_character}_{spell['name']}_{i}",
        )

        if new_prep_state != current_prep_state:
            for s in data["spells"]:
                if (
                    s["name"] == spell["name"]
                    and s["character"] == selected_character
                ):
                    s["prepared"] = new_prep_state
            save_data(data)
            st.rerun()

        st.markdown(
            f"**Domain:** {spell_domain_val} | **School:** {spell['school']} | **Casting Time:** {spell['casting_time']} | **Duration:** {spell.get('duration', 'Instantaneous')} | **Range:** {spell['range']} | **Ritual:** {spell.get('ritual', 'No')} | **Components:** {spell['components']}"
        )
        st.markdown("---")
        st.write(spell["description"])

        # Delete Button
        if st.button(
            f"🗑️ Delete {spell['name']}",
            key=f"del_{selected_character}_{spell['name']}_{i}",
        ):
            data["spells"] = [
                s
                for s in data["spells"]
                if not (
                    s["name"] == spell["name"]
                    and s["character"] == selected_character
                )
            ]
            save_data(data)
            st.success(f"Deleted '{spell['name']}'!")
            st.rerun()
