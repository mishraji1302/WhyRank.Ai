import app  # noqa: F401  # Configure joblib before importing sklearn/joblib.
from joblib import parallel


def test_joblib_multiprocessing_disabled_for_api_process():
    assert parallel.mp is None
    assert parallel.cpu_count() == 1
