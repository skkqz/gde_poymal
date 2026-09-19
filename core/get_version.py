import tomllib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


try:
    from importlib.metadata import version as _pkg_version
    VERSION = _pkg_version('gde-poymal')
except Exception:
    with open(BASE_DIR / 'pyproject.toml', 'rb') as _f:
        VERSION = tomllib.load(_f)['project']['version']


VERSION_APP = VERSION
