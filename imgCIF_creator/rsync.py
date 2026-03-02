import signal
import tempfile
from pathlib import Path
from subprocess import run, CalledProcessError, Popen, PIPE

def is_folder(url):
    if url.endswith("/"):
        return True

    res = run(["rsync", "--list-only", url], capture_output=True, text=True)
    res.check_returncode()
    return res.stdout.strip().startswith("d")


def get_file_list(url):
    res = run(["rsync", "--list-only", "--no-h", url], capture_output=True, text=True)
    res.check_returncode()
    lines = res.stdout.strip().splitlines(keepends=False)
    if not url.endswith("/") and len(lines) == 1 and lines[0].startswith('d'):
        # It's a directory, list its contents
        url += "/"
        res = run(["rsync", "--list-only", "--no-h", url], capture_output=True, text=True)
        res.check_returncode()
        lines = res.stdout.strip().splitlines(keepends=False)

    # split -> (mode, size, date, time, name)
    # Exclude directories, return the URL & size for the file
    return [((url + t[-1]) if url.endswith("/") else url, int(t[1]))
            for l in lines if (t := l.strip().split(None, 4))[0][0] == '-']


def total_size(file_list):
    return sum(s for _, s in file_list)

def download(folder_url, dest: Path, rel_paths):
    folder_url = folder_url.rstrip("/") + "/"  # Ensure trailing /
    with tempfile.NamedTemporaryFile() as tf:
        for p in rel_paths:
            tf.write(p.encode('utf-8') + b'\0')
        tf.flush()
        popen = Popen([
            "rsync", "--info=name", "--files-from", tf.name, "--from0",
            folder_url, str(dest)
        ], stdin=PIPE, stdout=PIPE)
        try:
            popen.stdin.close()
            for i, line in enumerate(popen.stdout):
                yield i  # For progress monitoring
        except:
            popen.send_signal(signal.SIGTERM)
            raise
        else:
            # stdout was closed, so the process is probably already finished
            if (ec := popen.wait(5)) != 0:
                raise CalledProcessError(ec, popen.args)
