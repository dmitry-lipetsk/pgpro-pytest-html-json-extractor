#!/bin/bash
set -euo pipefail  # Our "strong control"

: "${PYTEST_HTML_SPEC:?Error: PYTEST_HTML_SPEC environment variable is not set!}"

echo "--- Initializing test run ---"
echo "Python version: $(python --version)"
echo "Pytest-html spec: $PYTEST_HTML_SPEC"

# prepare python environment
VENV_PATH="/tmp/merger_venv"
rm -rf $VENV_PATH
python -m venv "${VENV_PATH}"
export VIRTUAL_ENV_DISABLE_PROMPT=1
source "${VENV_PATH}/bin/activate"
pip install bs4 pytest pytest-xdist

if [ "$PYTEST_HTML_SPEC" = "default" ]; then
  pip install "pytest-html>=4.0.2"
else
  pip install "pytest-html${PYTEST_HTML_SPEC}"
fi

# run builtin tests
python3 -m pytest -l -vvv -n 4 tests

set +eux
