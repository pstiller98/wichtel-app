import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import random
import json
import os
from pathlib import Path

# Seitenkonfiguration
st.set_page_config(page_title="🎄 Weihnachtswichteln", page_icon="🎁", layout="centered")

# Lade Konfiguration aus config.yaml
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# JSON-Datei für persistente Speicherung
DATA_FILE = 'wichtel_data.json'

# Hilfsfunktionen für Datei-Speicherung
def load_data():
    """Lädt die Wichtel-Daten aus der JSON-Datei"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return create_empty_data()
    return create_empty_data()

def create_empty_data():
    """Erstellt eine leere Datenstruktur"""
    return {
        'assignments': {},
        'wishlists': {
            'paul': '',
            'katrin': '',
            'joachim': '',
            'amon': ''
        },
        'assignment_done': False
    }

def save_data(data):
    """Speichert die Wichtel-Daten in die JSON-Datei"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Daten beim Start laden
if 'data_loaded' not in st.session_state:
    data = load_data()
    st.session_state.assignments = data['assignments']
    st.session_state.wishlists = data['wishlists']
    st.session_state.assignment_done = data['assignment_done']
    st.session_state.data_loaded = True

# Authentifizierung mit korrekten Parametern
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login - neuere Version gibt nichts zurück, speichert direkt in session_state
authenticator.login()

# Authentication Status aus session_state holen
name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

if authentication_status == False:
    st.error('Username/Passwort ist falsch')
elif authentication_status == None:
    st.warning('Bitte Username und Passwort eingeben')
elif authentication_status:
    # Header
    st.title("🎄 Weihnachtswichteln 2025 🎁")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f'Willkommen *{name}*!')
    with col2:
        authenticator.logout()
    
    st.divider()
    
    # Admin Bereich
    if config['credentials']['usernames'][username].get('role') == 'admin':
        st.header("👑 Admin-Bereich")
        
        st.info("Als Admin kannst du die Wichtel-Auslosung starten und verwalten.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎲 Auslosung starten", type="primary", use_container_width=True):
                participants = ['paul', 'katrin', 'joachim', 'amon']
                receivers = participants.copy()
                random.shuffle(receivers)
                
                # Sicherstellen, dass niemand sich selbst zieht
                max_attempts = 100
                attempt = 0
                while attempt < max_attempts:
                    valid = True
                    for i, giver in enumerate(participants):
                        if giver == receivers[i]:
                            valid = False
                            break
                    
                    if valid:
                        break
                    
                    random.shuffle(receivers)
                    attempt += 1
                
                # Zuordnung speichern
                st.session_state.assignments = {giver: receiver for giver, receiver in zip(participants, receivers)}
                st.session_state.assignment_done = True
                
                # In Datei speichern
                save_data({
                    'assignments': st.session_state.assignments,
                    'wishlists': st.session_state.wishlists,
                    'assignment_done': True
                })
                
                st.success("✅ Auslosung erfolgreich durchgeführt und gespeichert!")
                st.balloons()
        
        with col2:
            if st.button("🔄 Auslosung zurücksetzen", use_container_width=True):
                st.session_state.assignments = {}
                st.session_state.assignment_done = False
                
                # In Datei speichern
                save_data({
                    'assignments': {},
                    'wishlists': st.session_state.wishlists,
                    'assignment_done': False
                })
                
                st.success("✅ Auslosung wurde zurückgesetzt!")
        
        # Status anzeigen
        st.divider()
        if st.session_state.assignment_done:
            st.success("📋 Auslosung ist aktiv - alle Teilnehmer können nun ihre Zielperson sehen!")
            
            with st.expander("🔍 Zuordnungen anzeigen (nur für Admin)"):
                for giver, receiver in st.session_state.assignments.items():
                    st.write(f"**{giver.capitalize()}** beschenkt **{receiver.capitalize()}**")
        else:
            st.warning("⏳ Auslosung noch nicht durchgeführt")
        
        # Wunschlisten-Übersicht
        st.divider()
        st.subheader("📝 Alle Wunschlisten")
        for user, wishlist in st.session_state.wishlists.items():
            with st.expander(f"Wunschliste von {user.capitalize()}"):
                if wishlist:
                    st.write(wishlist)
                else:
                    st.write("*Noch keine Wunschliste eingetragen*")
    
    # User Bereich
    else:
        # Tabs für bessere Übersicht
        tab1, tab2 = st.tabs(["🎁 Mein Wichtelpartner", "📝 Meine Wunschliste"])
        
        with tab1:
            st.header("🎁 Dein Wichtelpartner")
            
            if st.session_state.assignment_done and username in st.session_state.assignments:
                target = st.session_state.assignments[username]
                
                st.success(f"Du beschenkst: **{target.capitalize()}** 🎅")
                
                st.divider()
                st.subheader(f"📋 Wunschliste von {target.capitalize()}")
                
                target_wishlist = st.session_state.wishlists.get(target, '')
                if target_wishlist:
                    st.info(target_wishlist)
                else:
                    st.warning(f"{target.capitalize()} hat noch keine Wunschliste eingetragen.")
            else:
                st.info("⏳ Die Auslosung wurde noch nicht durchgeführt. Bitte warte, bis der Admin die Auslosung startet!")
        
        with tab2:
            st.header("📝 Deine Wunschliste")
            
            st.write("Hier kannst du deine Wünsche eintragen, die dein Wichtelpartner sehen kann:")
            
            current_wishlist = st.session_state.wishlists.get(username, '')
            
            wishlist_input = st.text_area(
                "Deine Wünsche:",
                value=current_wishlist,
                height=200,
                placeholder="z.B.:\n- Ein gutes Buch\n- Schokolade\n- Warme Socken\n- Überraschung!"
            )
            
            if st.button("💾 Wunschliste speichern", type="primary"):
                st.session_state.wishlists[username] = wishlist_input
                
                # In Datei speichern
                save_data({
                    'assignments': st.session_state.assignments,
                    'wishlists': st.session_state.wishlists,
                    'assignment_done': st.session_state.assignment_done
                })
                
                st.success("✅ Deine Wunschliste wurde gespeichert!")
                st.balloons()
    
    # Footer
    st.divider()
    st.caption("🎄 Frohe Weihnachten und viel Spaß beim Wichteln! 🎁")
    
    # Debug Info für Admin
    if config['credentials']['usernames'][username].get('role') == 'admin':
        with st.expander("🔧 Debug Info (nur für Admin)"):
            st.caption(f"Daten werden gespeichert in: `{os.path.abspath(DATA_FILE)}`")
            if os.path.exists(DATA_FILE):
                st.caption(f"✅ Datei existiert und ist {os.path.getsize(DATA_FILE)} Bytes groß")