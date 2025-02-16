import streamlit as st

landing_page = st.Page("landingpage2.py", title="HeyDoc Chatbot", icon=":material/home:")
perso_page = st.Page("personnal_info.py", title="Personal Info", icon=":material/settings_accessibility:")

pg = st.navigation([landing_page, perso_page])
pg.run()
