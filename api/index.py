from flask import Flask
from flask import send_file, render_template
from flask import request
from subprocess import run
from tempfile import NamedTemporaryFile
from html import unescape
from os import urandom, remove
from os.path import join
from tempfile import gettempdir
from traceback import format_exc

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("index.html")

global_rules = open(join("data", "global.ty")).read() + "\n"
compiler = join("data", "typst")
tmpdir = gettempdir()

def process(input: str) -> str:
    try:
        input = unescape(input)
        typst = open(join(tmpdir, urandom(8).hex()), "w+")
        typst.write(global_rules)
        typst.write(input)
        typst.flush()
        svg = open(join(tmpdir, urandom(8).hex() + ".svg"), "a+")
        output = run(f"{compiler} compile -f svg {typst.name} {svg.name}", shell=True, capture_output=True)
        # output = svg.read()
        remove(typst.name)
        remove(svg.name)
    except Exception as e:
        return format_exc()
    return output

@app.post("/compile")
def compile():
    return process(request.form.get("innerHTML", default="*something went wrong*"))

@app.post("/hint")
def hint():
    hints = list(request.form.items())
    hints = list(map(lambda entry: (entry[0], process(entry[1])), hints))
    return render_template("hints.html", hints=hints)

@app.post("/solution")
def solution():
    solution = process(request.form.get("innerHTML", default="*something went wrong*"))
    return render_template("solution.html", solution=solution)