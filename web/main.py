# Copyright European XFEL GmbH, ANSTO & Utrecht University, 2024-2026
# Licensed under the EUPL-1.2 or later

import streamlit as st

download_page = st.Page("download.py", title="ImgCIF from downloads", icon=":material/download:")
expt_page = st.Page("expt.py", title="ImgCIF from DIALS .expt", icon=":material/upload:")
makecbf_page = st.Page("make_cbf.py", title="Convert files to CBF", icon=":material/file_export:")

pg = st.navigation([download_page, expt_page, makecbf_page])
pg.run()
