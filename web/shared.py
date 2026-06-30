# Copyright European XFEL GmbH, ANSTO & Utrecht University, 2024-2026
# Licensed under the EUPL-1.2 or later

from pathlib import Path

import streamlit as st

def acknowledgements():
    images_dir = Path(__file__).parent
    st.sidebar.image(images_dir / "oscars_logo.svg")

    st.sidebar.html("""\
    <small>This service has been developed with support from the <a href="https://oscars-project.eu/">OSCARS project</a>,
    which has received funding from the European Commission’s Horizon Europe
    Research and Innovation programme under grant agreement No. 101129751.</small>
    """)

    st.sidebar.image(images_dir / "iucr_logo.png")

    st.sidebar.html("""\
    <small>The service is hosted by the IUCr.</small>
    """)
