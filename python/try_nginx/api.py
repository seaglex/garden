import flask
import json
import pdb

app = flask.Flask(__name__)

def wrap(key, value):
    return json.dumps({
        key: value,
        "headers": flask.request.headers.to_list(),
        "host": flask.request.host,
    })

@app.route("/user")
def users():
    return wrap("users", [1, 2, 3])

@app.route("/user/<id>")
def user(id):
    # pdb.set_trace()
    return wrap("user", id)

@app.route("/")
def main():
    return flask.redirect("/user")

if __name__ == "__main__":
    app.run(debug=True)
