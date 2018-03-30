import flask
import time
import random
import logging
import json
import datetime as dt
import sys


app = flask.Flask(__name__)
logger = app.logger
logger.addHandler(logging.FileHandler("flask_slow_fast_call.txt", mode="a"))
logger.setLevel(logging.INFO)

def get_duration():
    return (dt.datetime.now() - flask.g.start).total_seconds() * 1000


@app.before_request
def before_request():
    flask.g.start = dt.datetime.now()


class Statistic(object):
    _fast_count = 0
    _slow_count = 0

    @staticmethod
    def get_fast_count():
        Statistic._fast_count += 1
        return Statistic._fast_count

    @staticmethod
    def get_slow_count():
        Statistic._slow_count += 1
        return Statistic._slow_count


class Work(object):
    @staticmethod
    def hard_work():
        time.sleep(random.randint(1, 5))
        return Statistic.get_slow_count()

    @staticmethod
    def easy_work():
        return Statistic.get_fast_count()

@app.route("/flask/fast/<int:id_>")
def fast_call(id_):
    logger.info("fast_call/in/%d:%s" % (id_, get_duration()))
    result = {"count": Work.easy_work()}
    result["duration"] = get_duration()
    logger.info("fast_call/out/%d:%s" % (id_, json.dumps(result)))
    return flask.jsonify(result)

@app.route("/flask/slow/<int:id_>")
def slow_call(id_):
    logger.info("slow_call/in/%d:%s" % (id_, get_duration()))
    result = {"count": Work.hard_work()}
    result["duration"] = get_duration()
    logger.info("slow_call/out/%d:%s" % (id_, json.dumps(result)))
    return flask.jsonify(result)


if __name__ == "__main__":
    app.run()
