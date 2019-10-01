import configparser
from pathlib import Path
import shutil

from .log import logger


def load_setup_cfg():
    setup_cfg = configparser.ConfigParser()
    setup_cfg.read('setup.cfg')
    return setup_cfg


def find_files(globs, service):
    files = []
    log = logger()

    for glob in globs:
        matches = map(str, Path().glob(glob))
        files += list(matches)

    # NOTE: This is the wrong place for this log call
    log.info('Uploading to %s: %s', service, ', '.join(files))
    return files


def try_delete(path):
    if Path(path).is_dir():
        shutil.rmtree(path)
    elif Path(path).exists():
        raise RuntimeError("'{}' is not a directory".format(path))
