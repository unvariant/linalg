from flask import Flask
from flask import send_file, render_template
from flask import request
from subprocess import run
from tempfile import NamedTemporaryFile
from html import unescape
from os.path import join

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("index.html")

global_rules = open(join("data", "global.ty")).read() + "\n"
compiler = join("data", "typst")

def process(input: str) -> str:
    try:
        input = unescape(input)
        typst = NamedTemporaryFile()
        typst.write(global_rules.encode())
        typst.write(input.encode())
        typst.flush()
        svg = NamedTemporaryFile(mode="r+", suffix=".svg")
        run(f"{compiler} compile -f svg {typst.file.name} {svg.file.name}", shell=True, check=True)
        typst.close()
        output = svg.read()
        svg.close()
    except Exception as e:
        return f"An error occurred: {e}"
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