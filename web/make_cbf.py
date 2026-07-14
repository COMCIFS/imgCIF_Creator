import os
import os.path as osp
from pathlib import Path
from tarfile import TarFile
from tempfile import TemporaryDirectory

import streamlit as st
from dxtbx.model.experiment_list import ExperimentListFactory

from imgCIF_creator.core import make_cbf
from imgCIF_creator.helpers import fmt_bytes
from shared import acknowledgements

SIZE_LIMIT = 5 * (1024 ** 3)

upload_dir = Path(
    os.environ.get("MAKECBF_UPLOAD_DIR", "") or
    "/gpfs/exfel/data/scratch/kluyvert/makecbf-uploads"
)
upload_dir.mkdir(parents=True, exist_ok=True)

acknowledgements()

st.title("Convert files to CBF")

st.markdown("This will convert any files that [DIALS](https://dials.github.io/) "
            "can understand to CBF format. There is an upload limit of 5 GB; "
            "if this is an issue for you, please install the [command line version]"
            "(https://github.com/COMCIFS/imgCIF_Creator) to run locally.")

files = st.file_uploader("Upload data files", accept_multiple_files=True)

if not files:
    st.stop()

if (total_size := sum([uf.size for uf in files])) > SIZE_LIMIT:
    st.warning(f"Total upload of {fmt_bytes(total_size)} exceeds limit of "
               f"{fmt_bytes(SIZE_LIMIT)}.")
    st.stop()

@st.cache_resource(scope="session", on_release=lambda td: td.cleanup(), show_spinner="Saving files...")
def tmp_directory(uploaded_files):
    td = TemporaryDirectory(dir=upload_dir)
    input_dir = Path(td.name, "input")
    input_dir.mkdir()
    for uf in uploaded_files:
        print(uf.name)
        (input_dir / uf.name).write_bytes(uf.getbuffer())
    return td

workspace = tmp_directory(files).name

@st.cache_data(show_spinner="Reading files...")
def load_expt_list(paths):
    return ExperimentListFactory.from_filenames(paths)

expts = load_expt_list((osp.join(workspace, "input"),))

with st.spinner("Converting files..."):
    make_cbf(expts, frame_limit=None)

tar_path = osp.join(workspace, "converted.tar.gz")
with st.spinner("Compressing output..."):
    with TarFile(tar_path, "w") as tf:
        tf.add(osp.join(workspace, "CBF"), arcname="CBF")

f = open(tar_path, "rb")
st.download_button(
    "Download converted files", f, file_name="converted.tar.gz", mime="application/gzip"
)
