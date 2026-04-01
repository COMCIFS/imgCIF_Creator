import streamlit as st

download_page = st.Page("download.py", title="ImgCIF from downloads", icon=":material/download:")
expt_page = st.Page("expt.py", title="ImgCIF from DIALS .expt", icon=":material/upload:")

pg = st.navigation([download_page, expt_page])
pg.run()
