# Backed

Here is how you launch the project:

* Install UV for dependency and python management: https://pypi.org/project/uv/
* Make sure your WD is backend: ``cd backend``
* Then run ``uv sync``, this should:
  * Setup venv
  * install/switch to python 3.9
  * install dependencies
* on vscode, need to activate the newly created venv from terminal: run ``source .venv/bin/activate`` to do so
* run ``python3 app.py`` from terminal to launch project