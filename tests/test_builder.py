from functools import partial
from pathlib import Path
from typing import Literal
import logging

import pytest

from bork import builder
from utils import cd


def is_beneath(child: Path, parent: Path) -> Path | Literal[False]:
    try:
        return child.relative_to(parent)
    except ValueError:
        return False

def _artefact(dst, artefact, suffix = ""):
    assert isinstance(artefact, Path)
    assert artefact.name.endswith(suffix)

    match is_beneath(artefact, dst):
        case False:
            raise ValueError(f"'{artefact}' not in directory '{dst}'")
        case rel if len(rel.parts) == 1:
            return
        case rel:
            raise ValueError(f"'{rel}' is not directly in directory")


@pytest.mark.slow
def test_builder_cwd(project_src, tmp_path):
    "Ensure that `builder` does not depend on the current working directory"
    log = logging.getLogger(__name__ + ".test_builder_cwd")
    dst = (tmp_path / 'dist').resolve()
    artefact = partial(_artefact, dst)

    with cd(tmp_path):
      log.info(f"Preparing builder from {Path.cwd()}")
      with builder.prepare(project_src, dst.relative_to(Path.cwd())) as b:
          with cd(tmp_path / "metadata", mkdir = True):
              log.info(f"Building metadata from {Path.cwd()}")
              meta = b.metadata()

              # Can't actually check the object implements the protocol
              for k in ("name", "version", "Metadata-Version"):
                  assert k in meta, f"built metadata does not contain '{k}'"

          with cd(tmp_path / "sdist", mkdir = True):
              log.info(f"Building source distribution from {Path.cwd()}")
              artefact(b.build("sdist"), ".tar.gz")

          with cd(tmp_path / "wheel", mkdir = True):
              log.info(f"Building wheel from {Path.cwd()}")
              artefact(b.build("wheel"), ".whl")
