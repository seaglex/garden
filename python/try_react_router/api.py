import flask


app = flask.Flask(__name__)

@app.route("/react_router/<path:path>")
@app.route("/react_router/", defaults={"path":""})
def react_router(path):
    return flask.render_template("router.html")

@app.route("/")
def main():
    return "try /react_router"

if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=True)
