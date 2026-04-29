import re
import posixpath
from numbers import Real
from urllib.parse import urlsplit, urlunsplit

from .core import ArchiveUrl, DirectoryUrl

DOI_RULES = [
    # Download URL regex -> DOI template
    (r"https://zenodo\.org/records/(\d+)", "10.5281/zenodo.{}"),
    (r"\w+://[\w\-.]+/10\.15785/SBGRID/(\d+)", "10.15785/SBGRID/{}"),  # Various sbgrid domains
    (r"https://xrda\.pdbj\.org/rest/public/entries/download/(\d+)", "10.51093/xrd-{:05}"),
]


def guess_doi(download_info):
    """Guess a DOI for common repositories from the download URLs"""
    urls = []
    for loc in download_info:
        if isinstance(loc, ArchiveUrl):
            urls.append(loc.url)
        elif isinstance(loc, DirectoryUrl):
            urls.append(loc.url_base)

    if not urls:
        return ""

    for url_pat, doi_template in DOI_RULES:
        matches = [re.match(url_pat, u) for u in urls]
        if all(matches):
            id_part = matches[0][1]
            if all(m[1] == id_part for m in matches[1:]):
                return doi_template.format(id_part)

    return ""


def extrapolate_sequence(s0: str, s1: str, length: int):
    """Extrapolate a sequence of strings, e.g. URLs, with an embedded number"""
    matched0 = re.split(r"(\d+)", s0)
    matched1 = re.split(r"(\d+)", s1)
    if len(matched0) != len(matched1):
        return

    if (
        len(
            diffs := [
                i for i, (p0, p1) in enumerate(zip(matched0, matched1)) if p0 != p1
            ]
        )
        != 1
    ):
        return  # No difference, or >1 piece differs
    if (diff_ix := diffs[0]) % 2 == 0:
        return  # The difference is in a non-numeric part

    width = len(matched0[diff_ix])
    n0 = int(matched0[diff_ix])  # First number in sequence
    if int(matched1[diff_ix]) != n0 + 1:
        return  # Not increasing by 1

    for i in range(2, length):
        pieces = matched0.copy()
        pieces[diff_ix] = f"{n0 + i:0{width}}"
        yield "".join(pieces)


def base_url_and_rel_paths(urls):
    """Given a list of URLs where only the path changes, find the common part"""
    s0 = urlsplit(urls[0])
    if len(urls) == 1:
        if s0.path.endswith("/"):
            path, slash = s0.path[:-1], "/"
        else:
            path, slash = s0.path, ""
        dirname, basename = posixpath.split(path)

        common_url = urlunsplit((s0.scheme, s0.netloc, dirname, s0.query, ''))
        return common_url, [basename + slash]

    fixed = (s0.scheme, s0.netloc, s0.query)
    paths = [s0.path]
    for u in urls[1:]:
        s = urlsplit(u)
        if (s.scheme, s.netloc, s.query) != fixed:
            raise ValueError("Only the path of URLs may vary")
        paths.append(s.path)
    common_path = posixpath.commonpath(paths)
    common_url = urlunsplit((s0.scheme, s0.netloc, common_path, s0.query, ''))
    return common_url, [
        # Preserve trailing slashes, they are relevant for rsync
        posixpath.relpath(p, common_path) + ("/" if p.endswith("/") else "")
        for p in paths
    ]



def fmt_bytes(n: Real) -> str:
    n = float(n)
    for suffix in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if n < 1024:
            break
        n /= 1024

    return f'{n:.1f} {suffix}'
