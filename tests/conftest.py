import os
import tempfile

os.environ.setdefault("LSPD_DATA_DIR", tempfile.mkdtemp(prefix="lspd-test-"))
