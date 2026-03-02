Create ImgCIF metadata from raw data, or a DIALS ``.expt`` file.

## Setup

1. If you don't already have the `conda` command, download and install
   [Miniforge](https://conda-forge.org/download/).
2. Create the environment:

```shell
conda env create --file conda-env.yml
```

3. Activate the environment:

```shell
conda activate imgcif-creator
```

Activating the environment is temporary: if you open another terminal, you'll
need to run this step again.

## Run in a terminal

With the environment set up, run:

```shell
python -m imgCIF_creator.tui path/to/some/data
```

You can run it on files or folders of data in CBF, HDF5, TIFF or SMV format.
Alternatively, if you already have a DIALS `.expt` experiment file, you can use
that as input.

## Run the web interface

With the environment set up, run:

```shell
streamlit run streamlit-downloading.py
```

This will show a URL in the terminal to open in a browser.
This accepts the same data formats as in the terminal, but here you start with
the URLs to download them.
