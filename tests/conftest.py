import os, shutil, sys
import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "models"))
sys.path.insert(0, os.path.join(ROOT, "physics"))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: full-year or multi-run cases (deselect with -m 'not slow')")
    config.addinivalue_line("markers", "excel: needs LibreOffice to recalculate a workbook")
    config.addinivalue_line("markers", "js: needs node to run the web apps' engine")


def still_weather(T=0.0):
    """A year with constant outdoor temperature and no sun."""
    z = np.zeros(8760)
    return dict(T=np.full(8760, float(T)), GHI=z, DNI=z, DHI=z, cosz=-np.ones(8760), az=z, name="still")


@pytest.fixture(scope="session")
def london():
    import weather as wx
    return {v: wx.get(v) for v in ("typical", "hot")}


@pytest.fixture(scope="session")
def soffice():
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        pytest.skip("LibreOffice not installed")
    return exe
