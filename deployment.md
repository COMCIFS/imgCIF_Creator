The web interface is deployed on a VM hosted by IUCr.
The server is not directly reachable from the internet, but an nginx reverse
proxy exposes it as https://imgcif.iucr.org/ .

Key paths:

- Code: `/opt/imgcif/imgCIF_Creator`
- Conda environment: `/opt/imgcif/miniforge3/envs/imgcif-creator`
- Download cache: `/srv/imgcif-data/download-cache`
- Systemd unit file: `/etc/systemd/system/streamlit.service`

The service runs as the `imgcif` user. Logs are sent to the journal, and can
be viewed with `journalctl -u streamlit`.
