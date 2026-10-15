"""Run the whole project with one command.

    python run_all.py           check, clean, chart, test, summarise and build the report
    python run_all.py --serve   the same, then open the report at http://localhost:8000
    add --no-open to serve the report without opening a browser window

The raw data is already in the repository, so nothing is downloaded unless you run
scripts/fetch_data.py yourself.
"""
import http.server
import importlib.util
import subprocess
import sys
import time
import webbrowser
from functools import partial
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PORT = 8000

STEPS = [
    ("Check and clean the data", ["scripts/clean_data.py"]),
    ("Draw the charts", ["scripts/make_charts.py"]),
    ("Test real against made-up data", ["scripts/realism_check.py"]),
    ("Print the figures in the report", ["scripts/summary.py"]),
    ("Build the report page", ["scripts/build_site.py"]),
]


def run(title, arguments):
    print(f"\n=== {title} ===", flush=True)
    started = time.perf_counter()
    result = subprocess.run([sys.executable, *arguments], cwd=BASE_DIR)
    if result.returncode != 0:
        sys.exit(f"Stopped: '{title}' failed.")
    print(f"--- done in {time.perf_counter() - started:.1f} s", flush=True)


def main():
    for title, arguments in STEPS:
        run(title, arguments)

    # The tests need pytest, which is in requirements-dev.txt.
    if importlib.util.find_spec("pytest"):
        run("Run the tests", ["-m", "pytest", "-q"])
    else:
        print("\nSkipped the tests. Install them with: pip install -r requirements-dev.txt")

    print("\nAll steps finished. The report is in _site/index.html", flush=True)

    if "--serve" in sys.argv:
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(BASE_DIR / "_site"))
        # The threaded server keeps answering even when a browser holds a spare connection open.
        with http.server.ThreadingHTTPServer(("", PORT), handler) as server:
            url = f"http://localhost:{PORT}"
            print(f"Serving the report at {url}  (press Ctrl+C to stop)", flush=True)
            if "--no-open" not in sys.argv:
                webbrowser.open(url)
            server.serve_forever()


if __name__ == "__main__":
    main()
