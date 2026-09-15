"""pipalhub_magic

Jupyter Lab magic commands for trainings by Pipal Academy.

"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

import ipykernel
import markdown
import nbformat
import requests
import yaml
from jupyter_server import serverapp as app
from . import config

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


PROBLEM_ROOT = config.problem_root


class Problem:
    def __init__(self, name, metadata):
        self.name = name
        self.metadata = metadata
        self.title = self.metadata["title"]
        self.logger = _Logger()
        self.root = Path(PROBLEM_ROOT) / name

        self.problem_type = metadata.get("problem_type")
        self.script_name = metadata.get("script_name")

    @classmethod
    def find(cls, name):
        path = Path(PROBLEM_ROOT) / name / "problem.yml"
        metadata = yaml.safe_load(path.open())
        return cls(name, metadata)

    def open(self, path):
        return self.joinpath(path).open()

    def joinpath(self, path):
        p = Path(PROBLEM_ROOT) / self.name / path
        return p

    def get_description(self):
        return self.open("description.md").read()

    def get_initial_code(self):
        files = self.metadata["files"].get("code", [])
        if files:
            return self.open(files[0]).read()

    def get_description_html(self):
        desc = self.get_description()
        return self.markdown(desc)

    def markdown(self, text):
        return markdown.markdown(text, extensions=["fenced_code"])

    def _repr_html_(self):
        return f"""
        <strong>Problem: {self.title}</strong>

        <p>{self.get_description_html()}
        </p>

        <p>You can verify your solution using:
        <pre>%verify_problem {self.name}</pre>
        </p>
        """

    def __repr__(self):
        return f"<Probem: {self.name}>"

    def verify(self, env):
        """Verify if the problem has been solved correctly.

        The env is the globals env of the user from the notebook.
        """
        status = self._verify(env)

        self.notify_status(status)

    def notify_status(self, status):
        # XXX-Anand: FIXME later
        return

        url = "https://engage.pipal.in/api/method/jupyter-problem-tracker"
        data = {
            "training": "zeomega-python",
            "user": os.getenv("USER"),
            "notebook": _get_notebook_name(),
            "problem": self.name,
            "status": status,
            "output": "\n".join(self.logger.lines),
        }
        requests.post(url, json=data).json()

    def _verify(self, env):
        func_name = self.metadata.get("function_name")
        script_name = self.metadata.get("script_name")

        if func_name is None and script_name is None:
            self.logger.log("Sorry, verification is not supported for this problem.")
            return "NOT SUPPORTED"

        if func_name and func_name not in env:
            self.logger.log(f"ERROR: Unable to find function with name {func_name}.")
            return "notfound"
        if script_name and not Path(script_name).exists():
            self.logger.log(f"ERROR: Unable to find program {script_name}.")
            return "notfound"

        passed = True

        checks = self.read_checks()
        print("Found", len(checks), "checks")
        for check in checks:
            check_passed = check.run(env)
            passed = passed and check_passed

        if passed:
            self.logger.log(f"🎉 Congratulations! You have successfully solved problem {self.name}!!")
            return "pass"
        else:
            self.logger.log(f"💥 Oops! Your solution to problem {self.name} is incorrect or incomplete.")
            return "fail"

    def read_checks(self):
        return [
            Check.load(spec, logger=self.logger, problem=self) for spec in yaml.safe_load_all(self.open("checks.yml"))
        ]


class Check:
    def __init__(self, spec, logger=None, problem=None):
        self.spec = spec
        self.logger = logger or _Logger()
        self.problem = problem

    @staticmethod
    def load(spec, logger=None, problem=None):
        if "code" in spec:
            return FunctionCheck(spec, logger=logger, problem=problem)
        elif "command" in spec:
            return CommandCheck(spec, logger=logger, problem=problem)
        else:
            raise ValueError(f"Invalid Check spec: {spec!r}")

    def run(self, env):
        raise NotImplementedError()


class FunctionCheck(Check):
    def __init__(self, spec, logger=None, problem=None):
        super().__init__(self, logger=logger, problem=problem)
        self.setup_code = spec.get("setup_code")
        self.code = spec["code"]
        self.name = spec.get("name") or self.code
        self.expected = spec["expected"]

        # hack to allow multi-line code using mode "exec"
        self._mode = spec.get("mode", "eval")

    def do_eval(self, code, env):
        env = env.copy()
        if self._mode == "eval":
            if self.setup_code:
                exec(self.setup_code, env)
            return eval(self.code, env)
        elif self._mode == "exec":
            exec(self.code, env)

            # hack to specify expected in code
            if "_expected" in env:
                self.expected = env["_expected"]

            return env["result"]
        else:
            raise ValueError(f"Invalid mode: {self._mode}")

    def run(self, env):
        env = dict(env)

        p = self.problem and self.problem.joinpath("_checks.py")
        if p.exists():
            exec(p.read_text(), env)

        try:
            result = self.do_eval(self.code, env)
        except Exception:
            self.logger.log(f"✗ {self.name}")
            sys.stdout.flush()
            traceback.print_exc()
            sys.stderr.flush()
            return False

        if result == self.expected:
            self.logger.log(f"✓ {self.name}")
            return True
        else:
            self.logger.log(f"✗ {self.name}")
            self.logger.log(f"  expected: {self.expected!r}")
            self.logger.log(f"  found: {result!r}")
            return False


class CommandCheck(Check):
    def __init__(self, spec, logger=None, problem=None):
        super().__init__(self, logger=logger, problem=problem)

        self.command = spec["command"]
        self.name = spec.get("name") or self.command
        self.sort_output = spec.get("sort_output", False)
        self.expected_output_print = ""
        self.expected_output = self.process_expected_output(spec.get("expected_output"), self.sort_output)
        self.expected_output_print = self.expected_output
        if self.sort_output:
            self.expected_output = self.sort_output_lines(self.expected_output)

        self.test = spec.get("test")

    def process_expected_output(self, expected_output, sort_output):
        if expected_output is None:
            return None
        if isinstance(expected_output, dict):
            cmd = expected_output["command"]

            cmd = cmd.format(PROBLEM_ROOT=self.problem.root)

            p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, check=False)
            return self.ignore_trailing_space(p.stdout.strip("\n"))
        else:
            return expected_output.strip("\n")

    def sort_output_lines(self, output):
        lines = output.splitlines()
        return "\n".join(sorted(lines))

    def ignore_trailing_space(self, text):
        lines = [line.rstrip() for line in text.splitlines()]
        return "\n".join(lines)

    def run(self, env):
        env = env.copy()
        # print(f"$ {self.command}")
        p = subprocess.run(
            self.command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
        output = p.stdout.strip("\n")
        output = self.ignore_trailing_space(output)
        output_print = output

        if self.sort_output:
            output = self.sort_output_lines(output)

        if self.expected_output is not None:

            # XXX-Anand: Work-around to deal with YAML when there are leading spaces in the first line
            # The trick is to replace the first space with an _ and the following code replaces that back to a space.
            if self.expected_output.startswith("_"):
                self.expected_output = self.expected_output.replace("_", " ", 1)

            if output == self.expected_output:
                self.logger.log(f"✓ {self.name}")
                return True
            else:
                self.logger.log(f"✗ {self.name}")
                self.logger.log(f"Expected:\n{self.expected_output_print}")
                self.logger.log(f"Found:\n{output_print}")
                return False
        elif self.test:
            self.stdout = output
            return self.run_test()
        else:
            return True

    def run_test(self):
        try:
            env = {"stdout": self.stdout}
            p = self.problem and self.problem.joinpath("_checks.py")
            if p.exists():
                exec(p.read_text(), env)

            exec(self.test, env)
        except Exception:
            self.logger.log(f"✗ {self.name}")
            sys.stdout.flush()
            traceback.print_exc()
            sys.stderr.flush()
            return False
        else:
            self.logger.log(f"✓ {self.name}")
            return True


class _Logger:
    """Simple logger to capture the logged output."""

    def __init__(self):
        self.lines = []

    def log(self, line):
        self.lines.append(line)
        print(line)
