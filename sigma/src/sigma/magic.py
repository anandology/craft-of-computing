"""
Jupyter Lab magic commands for trainings by Pipal Academy.
"""

import os

import ipykernel
from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class, needs_local_scope
from IPython.display import display

from .problems import Problem

__version__ = "0.1.0"


def create_new_cell(contents):
    from IPython.core.getipython import get_ipython

    shell = get_ipython()

    payload = dict(
        source="set_next_input",
        text=contents,
        replace=False,
    )
    shell.payload_manager.write_payload(payload, single=False)


def _get_kernel_id():
    path = ipykernel.get_connection_file()
    return os.path.basename(path).split("-", 1)[1].replace(".json", "")


def _get_notebook_name():
    """Return the name of the notebook file."""
    try:
        kid = _get_kernel_id()

        for s in app.list_running_servers():
            url = s["url"] + "api/sessions"
            notebooks = requests.get(url, params={"token": s["token"]}).json()
            for nb in notebooks:
                if nb["kernel"]["id"] == kid:
                    return nb["notebook"]["path"]
    except Exception:
        pass


@magics_class
class PipalMagics(Magics):
    @line_magic
    def load_problem(self, arg):
        """Loads a problem into the current cell."""
        # problem_text = f"**Problem: {arg}**"
        # contents = "# %load_problem " + arg
        # self.shell.set_next_input(contents, replace=True)

        problem = Problem.find(arg)
        display(problem)

        if problem.problem_type == "script":
            create_new_cell(f"%%file {problem.script_name}\n# your code here\n\n\n\n")
        else:
            code = problem.get_initial_code() or "# your code here\n\n\n\n"
            create_new_cell(code)

    @line_magic
    @needs_local_scope
    def verify_problem(self, name, local_ns=None):
        problem = Problem.find(name)
        problem.verify(local_ns)

def register():
    """Registers these magic commands with Ipython
    """
    ipython = get_ipython()
    ipython.register_magics(PipalMagics)
