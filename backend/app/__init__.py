"""WhyRank application package configuration."""

import os

# This service uses small local ranking workloads, not joblib process pools.
# Disable joblib multiprocessing before sklearn/joblib are imported so worker
# processes cannot leave loky semaphore resources behind at interpreter exit.
os.environ.setdefault("JOBLIB_MULTIPROCESSING", "0")
