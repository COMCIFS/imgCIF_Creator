import io
import os.path
from pathlib import Path
from urllib.parse import urlsplit

import h5py
import streamlit as st
import requests
from dxtbx.model.experiment_list import ExperimentListFactory

# Import imgCIF_creator from the nearby folder
from imgCIF_creator.core import (
    find_hdf5_images,
    guess_archive_type, guess_file_type, make_cif, ArchiveUrl, DirectoryUrl
)
from imgCIF_creator.helpers import (
    extrapolate_sequence,  guess_doi, base_url_and_rel_paths
)


def input_url_validated(label):
    if not (url := st.text_input(label)):
        st.stop()
    return check_url(url)

def check_url(url, message="Checking URL..."):
    try:
        with st.spinner(message):
            resp = requests.get(url, stream=True)
    except requests.RequestException as e:
        st.text(e)
        st.stop()
    else:
        if resp.status_code < 400:
            return url
        st.text(f"{resp.status_code}: {resp.reason}")
    st.stop()


def choose_archive_type(url):
    archive_type_guess = guess_archive_type(urlsplit(url).path)
    if (archive_type := st.pills(
            "Archive format", ["ZIP", "TGZ", "TBZ", "TXZ"], default=archive_type_guess
    )) is None:
        st.stop()
    return archive_type

def choose_archive_unpacked_root(file_path: Path) -> Path:
    options = [
        f"{file_path.relative_to(p)}"
        for p in file_path.parents[:-1]
    ]
    chosen = st.radio("Paths inside archive:", options=range(len(options)),
                      format_func=options.__getitem__)
    return file_path.parents[chosen]

def input_download_info():
    fmt_options = {
        "single": "A single archive (e.g. .zip or .tar.gz)",
        "scans": "One archive per scan",
        "separate": "Separate files, not in an archive",
    }
    if len(expts) == 1:
        del fmt_options["scans"]

    if not (download_opt := st.radio(
        "Download format", options=list(fmt_options), format_func=fmt_options.get
    )):
        st.stop()

    first_path = Path(expts[0].imageset.get_path(0))
    if download_opt == "single":
        url = input_url_validated("Archive URL: ")
        archive_type = choose_archive_type(url)
        base_dir = choose_archive_unpacked_root(first_path)
        return [ArchiveUrl(url, base_dir, archive_type)]
    elif download_opt == "scans":  # Archive per scan
        res = []

        st.markdown(f"Scan 1, starting with file `{first_path}`")
        first_url = input_url_validated("Archive 1 URL: ")
        archive_type = choose_archive_type(first_url)
        first_base_dir = choose_archive_unpacked_root(first_path)
        res.append(ArchiveUrl(first_url, first_base_dir, archive_type))
        if len(expts) <= 1:
            return res

        second_path = Path(expts[1].imageset.get_path(0))
        st.markdown(f"Scan 2, starting with file `{second_path}`")
        second_url = input_url_validated("Archive 2 URL: ")
        second_base_dir = choose_archive_unpacked_root(second_path)
        res.append(ArchiveUrl(second_url, second_base_dir, archive_type))
        if len(expts) <= 2:
            return res

        more_urls = list(extrapolate_sequence(first_url, second_url, len(expts)))
        if not more_urls:
            st.text("Could not find sequence from URLs")
        if second_base_dir == first_base_dir:
            more_base_dirs = [first_base_dir] * (len(expts) - 2)
        else:
            more_base_dirs = [
                Path(p)
                for p in extrapolate_sequence(
                    str(first_base_dir), str(second_base_dir), len(expts)
                )
            ]
            if not more_base_dirs:
                st.text("Could not find sequence from unpacked archive roots")

        for i in range(2, len(expts)):
            if more_urls:
                url = more_urls[i - 2]
                st.text(f"Scan {i + 1} URL: {url}")
                if i == len(expts) - 1:
                    check_url(url)
            else:
                url = input_url_validated(f"Scan {i + 1} URL: ")

            if more_base_dirs:
                base_dir = more_base_dirs[i - 2]
            else:
                eg_path = expts[i].imageset.get_path(0)
                base_dir = choose_archive_unpacked_root(eg_path)

            res.append(ArchiveUrl(url, base_dir, archive_type))

        return res

    else:  # Separate files
        if h5py.is_hdf5(first_path):
            first_path, *_ = next(find_hdf5_images(first_path))
        print("First data file:")
        print(" ", first_path)
        first_url = input_url_validated("URL for this file: ")

        last_path = Path(expts[-1].imageset.get_path(len(expts[-1].imageset) - 1))
        if h5py.is_hdf5(last_path):
            last_path, *_ = list(find_hdf5_images(last_path))[-1]

        base_dir = Path(os.path.commonpath([first_path, last_path]))
        levels_under_base = len(first_path.relative_to(base_dir).parts)
        base_url = first_url.rsplit("/", levels_under_base)[0]
        last_url = f"{base_url}/{last_path.relative_to(base_dir).as_posix()}"

        print("Last path:", last_path)
        print(f"Last URL (extrapolated):\n  {last_url}")
        check_url(last_url)
        print()

        print("Base URL:", base_url)
        print("Directory:", base_dir)
        return [DirectoryUrl(base_url, base_dir)]

def get_doi(download_info):
    guessed = guess_doi(download_info)
    if guessed:
        st.text(f"Data DOI (guessed from download URLs): {guessed}")

    if not (doi := st.text_input("DOI (optional):", value=guessed)):
        return None

    check_url(f"https://doi.org/{doi}", "Checking DOI resolves...")
    return doi

def input_file_type(name: str, dxtbx_fmt_cls):
    options = ["HDF5", "CBF", "TIFF", "SMV"]
    if (res := st.pills(
        "File type:", options=options, default=guess_file_type(name, dxtbx_fmt_cls))
    ) is None:
        st.stop()
    return res


st.title("ImgCIF creator")

st.markdown("This helps you create an ImgCIF file using a DIALS `.expt` experiment file. "
        "You can create this file using the `dials.import` command.")

if not (expt_file := st.file_uploader("Upload .expt file", type="expt")):
    st.stop()

with st.spinner("Reading file..."):
    expts = ExperimentListFactory.from_json(expt_file.read())

st.write(f"Found {len(expts)} experiment(s) with "
         f"{sum(len(e.imageset) for e in expts)} total images.\n")

download_info = input_download_info()
doi = get_doi(download_info)

imgset0 = expts[0].imageset
file_type = input_file_type(imgset0.get_path(0), imgset0.get_format_class())

st.divider()
# --------- Output ----------------

sio = io.StringIO()
make_cif(
    expts,
    sio,
    data_name="generated",
    locations=download_info,
    doi=doi,
    file_type=file_type,
    overload_value=None,
)
st.header("ImgCIF output")
st.download_button(
    "Download CIF file",
    sio.getvalue(),
    file_name="generated.cif",
    on_click="ignore",
    icon=":material/download:",
    type="primary"
)

st.text("Preview: showing a subset of the data")
sio = io.StringIO()
sio.write("# ImgCIF preview - incomplete data\n\n")
make_cif(
    expts,
    sio,
    data_name="preview",
    locations=download_info,
    doi=doi,
    file_type=file_type,
    overload_value=None,
    frame_limit=5,
)

st.code(sio.getvalue(), language=None)
