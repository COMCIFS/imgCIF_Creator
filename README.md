Create ImgCIF metadata from raw data, or a DIALS ``.expt`` file.

## Setup & usage (terminal)

1. If you don't already have the `conda` command, download and install
   [Miniforge](https://conda-forge.org/download/).
2. Install the package in a new environment:

```shell
conda create --yes -n imgcif-creator -c comcifs -c conda-forge imgcif_creator
```

3. Activate the environment:

```shell
conda activate imgcif-creator
```

Activating the environment is temporary: if you open another terminal, you'll
need to run this step again.

### Run

```shell
imgcif-creator path/to/some/data
```

You can run it on files or folders of data in CBF, HDF5, TIFF or SMV format.
Alternatively, if you already have a DIALS `.expt` experiment file, you can use
that as input.

## Web interface

https://imgcif.iucr.org/

To run a local copy of the web interface, e.g. for development:

1. Clone this repository.
2. Set up a conda environment

```shell
conda env create --file conda-env.yml
```

3. Activate the environment:

```shell
conda activate imgcif-creator
```

4. Launch the web interface:

```shell
streamlit run web/main.py
```

This will show a URL in the terminal to open in a browser.
The web interface has an option to start by downloading files (up to 5 GB),
or you can upload a DIALS `.expt` file.
