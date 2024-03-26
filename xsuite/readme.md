#### Xsuite Installation for Linux, MacOS or Windows:

1. **Conda installation:** Install conda from miniconda website https://docs.conda.io/projects/miniconda/en/latest/ or install from 'homebrew' if you are using MacOS.

2. **Create a build environment:**
conda init
conda create -n xsuite
conda activate xsuite

3. **Install cython:**
conda install python=3.11 wheel cython

4. **Install cpymad (see also at https://hibtc.github.io/cpymad/installation.html):**
pip install cpymad --only-binary cpymad

5. **Install Xsuite:**
pip install xsuite

6. **Install sixtracktools:**
pip install sixtracktools

7. **Some of the tests rely on pyheadtail to test the corresponding interface (only work for Linux):**
pip install pyheadtail


The manual of Xsuite see at https://xsuite.readthedocs.io/en/latest/installation.html.
The example of Xsuite see at https://github.com/xsuite/.