import signal
import tempfile
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from subprocess import run, CalledProcessError, Popen, DEVNULL, PIPE


def check_url(url) -> bool:
    res = run(["rsync", "--list-only", url], stdout=DEVNULL, stderr=DEVNULL)
    return res.returncode == 0


@contextmanager
def temp_file_list(names: list):
    with tempfile.NamedTemporaryFile() as tf:
        for p in names:
            tf.write(p.encode('utf-8') + b'\0')
        tf.flush()
        yield tf.name


@dataclass
class RsyncRequestFiles:
    """Files/folders we intend to download"""
    base_url: str
    rel_paths: list[str]

    def resolve(self) -> 'RsyncFileList':
        with temp_file_list(self.rel_paths) as file_list:
            res = run([
                "rsync",
                "--list-only",
                "--recursive",
                "--files-from", file_list,
                "--from0",
                "--no-h",  # no , in file sizes
                self.base_url,
                # Workaround: rsync currently needs a destination argument with
                # these options, even though it's not writing anything.
                # https://github.com/RsyncProject/rsync/pull/473
                tempfile.gettempdir(),  # Workaround
            ], stdout=PIPE, text=True, check=True)
        lines = res.stdout.strip().splitlines(keepends=False)
        files_sizes = []
        for l in lines:
            mode, size, date, time, name = l.strip().split(None, 4)
            if mode.startswith("-"):
                files_sizes.append((name, int(size)))

        return RsyncFileList(self.base_url, files_sizes)


@dataclass
class RsyncFileList:
    """File info from the server"""
    base_url: str
    files: list[tuple[str, int]]  # [(name, size)]

    def total_size(self):
        return sum([s for _, s in self.files])

    def file_url(self, i: int):
        self.base_url.rstrip("/") + "/" + self.files[i][0]

    def download(self, dest: Path):
        with temp_file_list([f for f, _ in self.files]) as file_list:
            popen = Popen([
                "rsync",
                "--info=name",
                "--files-from", file_list,
                "--from0",
                self.base_url,
                str(dest)
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
