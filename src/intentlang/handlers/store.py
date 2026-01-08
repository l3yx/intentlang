import json
import re
import time
import random
import string
from pathlib import Path
from ..models import IntentExecHandler, PythonExecResult, IntentBase, IntentResult


class Notebook:
    def __init__(self, path: Path | None = None):
        self._path = path
        self._index = 0
        if path and path.exists():
            self._data = json.loads(path.read_text())
        else:
            self._data = {"cells": [], "metadata": {}}

    def save(self, path: Path | None = None):
        target = path or self._path
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(
                self._data, indent=2, ensure_ascii=False))

    def add_raw(self, text: str):
        self._data["cells"].append({
            "cell_type": "raw",
            "metadata": {},
            "source": text.splitlines(keepends=True)
        })
        self.save()

    def add_code(self, text: str):
        self._data["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "source": text.splitlines(keepends=True)
        })
        self.save()

    def get_next_code(self) -> str:
        for i in range(self._index, len(self._data["cells"])):
            cell = self._data["cells"][i]
            if cell["cell_type"] == "code":
                self._index = i + 1
                return "".join(cell["source"])
        return "output = 'No more code cells available in cache.'"


class IntentStore(IntentExecHandler):
    def __init__(
        self,
        cache: bool = False,
        record: bool = True,
        cache_dir: str = ".intent_cache",
        record_dir: str = ".intent_record",
    ):
        self._cache = cache
        self._record = record
        self._cache_dir = cache_dir
        self._record_dir = record_dir
        self._cache_notebook: Notebook = None
        self._record_notebook: Notebook = None
        self._cache_path: Path = None
        self._intent_hash: str = None
        self._sanitized_goal: str = None

    def on_start(self, intent: IntentBase):
        self._intent_hash = intent._hash()
        self._sanitized_goal = re.sub(
            r'[^\w.-]+', '_', intent._goal).strip('._')

        if self._cache:
            self._cache_path = Path(self._cache_dir) / \
                f"{self._sanitized_goal}_{self._intent_hash}.ipynb"
            if self._cache_path.exists():
                self._cache_notebook = Notebook(self._cache_path)
            else:
                self._cache_notebook = Notebook()
                self._cache_notebook.add_raw(intent._build_ir())

        if self._record:
            timestamp = int(time.time())
            rand = ''.join(random.choices(
                string.ascii_lowercase + string.digits, k=6))
            record_filename = f"{timestamp}_{rand}.ipynb"
            record_path = Path(
                self._record_dir) / f"{self._sanitized_goal}_{self._intent_hash}" / record_filename
            self._record_notebook = Notebook(record_path)
            self._record_notebook.add_raw(intent._build_ir())

    def on_feedback(self, step: int, feedback: str) -> None | str:
        if self._cache and self._cache_notebook._path is not None:
            return self._cache_notebook.get_next_code()
        return None

    def on_code_response(self, step: int, code_response: str):
        if self._cache and self._cache_notebook._path is None:
            self._cache_notebook.add_code(code_response)
        if self._record:
            self._record_notebook.add_code(code_response)

    def on_exec_result(self, step: int, exec_result: PythonExecResult, feedback: str):
        if self._record:
            self._record_notebook.add_raw(feedback)

    def on_completed(self, result: IntentResult):
        if self._cache:
            self._cache_notebook.save(self._cache_path)

    def on_failed(self, error: Exception):
        pass
