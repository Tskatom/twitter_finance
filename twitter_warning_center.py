#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
from etool import queue, args, logs
import boto
from datetime import datetime, timedelta
import time
import hashlib
import json


__processor__ = 'twitter_warning_center'
log = logs.getLogger(__processor__)

COUNTRY_MARKET = {"Argentina": "MERVAL", "Brazil": "IBOV", "Chile": "CHILE65",
                  "Costa Rica": "CRSMBCT", "Colombia": "COLCAP",
                  "Mexico": "MEXBOL", "Panama": "BVPSBVPS",
                  "Peru": "IGBVL", "Venezuela": "IBVC"}


def checkTradingDay(t_domain, t_date, country):
    "Check weekend"
    week_day = datetime.strptime(t_date, "%Y-%m-%d").weekday()
    if week_day == 5 or week_day == 6:
        return False

    "Check holiday"
    sql = "select count(*) from s_holiday where country='%s' "
    sql += "and date ='%s'"
    sql = sql % (country, t_date)
    rs = t_domain.select(sql)
    count = 0
    for r in rs:
        count = int(r["Count"])

    return count == 0


def getTradingDate(t_domain, post_date, country):
    event_date = datetime.strptime(post_date, "%Y-%m-%d") + \
        timedelta(days=1)
    i = 0
    while True:
        str_date = datetime.strftime(event_date, "%Y-%m-%d")
        if checkTradingDay(t_domain, str_date, country):
            return str_date
        event_date += timedelta(days=1)
        i += 1
        if i > 10:
            return None


def warning_center(t_domain, tweet_analysis, warn_queue, threshold):
    z_value = float(tweet_analysis["z_value"])
    diff_mag = float(tweet_analysis["diff_mag"])
    country = tweet_analysis["country"]
    t_date = tweet_analysis["date"]
    #setup threashold
    if z_value >= threshold:
        warn = warning("Tweet Network Model Econo")
        event_date = getTradingDate(t_domain, t_date, country)
        probability = .6
        derived_from = {"derivedIds": []}
        comment = "Tweet network Model %s Date: %s Z_value: %.4f"\
            % (country, t_date, z_value)
        population = COUNTRY_MARKET.get(country)
        if diff_mag <= 0:
            event_type = "0412"
        else:
            event_type = "0411"

        warn.setEventDate(event_date)
        warn.setDerivedFrom(derived_from)
        warn.setPopulation(population)
        warn.setProbability(probability)
        warn.setEventType(event_type)
        warn.setComments(comment)
        warn.setLocation(country)
        #Test ----
        warn.setDate(t_date)

        warn.generateIdDate()
        warn.send(warn_queue)


def svm_warning(t_domain, tweet_analysis, warn_queue):
    country = tweet_analysis["country"]
    t_date = tweet_analysis["date"]
    event_date = getTradingDate(t_domain, t_date, country)
    probability = .6
    derived_from = {"derivedIds": []}
    comment = "Twiiter SVM Anormaly Detection Model"
    population = COUNTRY_MARKET.get(country)
    event_type = "0411"

    warn = warning("Tweet Network Model Econo")

    warn.setEventDate(event_date)
    warn.setDerivedFrom(derived_from)
    warn.setPopulation(population)
    warn.setProbability(probability)
    warn.setEventType(event_type)
    warn.setComments(comment)
    warn.setLocation(country)
    #Test ----
    warn.setDate(t_date)
    warn.generateIdDate()
    warn.send(warn_queue)
    return warn.warning


class warning():
    def __init__(self, model_name):
        self.warning = {}
        self.probability_flag = "confidenceIsProbability"
        self.warning[self.probability_flag] = "True"
        self.date_lab = "date"
        self.event_date_lab = "eventDate"
        self.population_lab = "population"
        self.probability_lab = "confidence"
        self.model_lab = "model"
        self.warning[self.model_lab] = model_name
        self.id_lab = "embersId"
        self.derived_lab = "derivedFrom"
        self.event_type_lab = "eventType"
        self.comment_lab = "comments"
        self.location_lab = "location"

    def send(self, pub_zmq):
        with queue.open(pub_zmq, "w", capture=True) as q_w:
            q_w.write(self.warning)
            time.sleep(1)

    def generateIdDate(self):
        if not self.id_lab in self.warning:
            self.warning[self.id_lab] = hashlib.sha1(str(self.warning))\
                .hexdigest()
        if not self.date_lab in self.warning:
            self.warning[self.date_lab] = datetime.utcnow().isoformat()

    def setEventDate(self, event_date):
        self.warning[self.event_date_lab] = event_date

    def setPopulation(self, population):
        self.warning[self.population_lab] = population

    def setProbability(self, probability):
        self.warning[self.probability_lab] = probability

    def setDerivedFrom(self, derived):
        self.warning[self.derived_lab] = derived

    def setEventType(self, event_type):
        self.warning[self.event_type_lab] = event_type

    def setComments(self, comment):
        self.warning[self.comment_lab] = comment

    def setDate(self, deliver_date):
        self.warning[self.date_lab] = deliver_date

    def setLocation(self, location):
        self.warning[self.location_lab] = location


def get_domain(conn, d_name):
    t_domain = conn.lookup(d_name)
    if t_domain is None:
        conn.create_domain(d_name)
        t_domain = conn.get_domain(d_name)
    return t_domain


def main():
    ap = args.get_parser()
    ap.add_argument('--level', type=str, default="0.6",
                    help='The threhold')
    ap.add_argument('--svm', action='store_true')
    ap.add_argument('--zmq', action='store_true')
    ap.add_argument('--surr', type=str, help="surrogate file")
    ap.add_argument('--warn', type=str, help="warning file")
    arg = ap.parse_args()

    logs.init(arg)
    queue.init(arg)
    assert arg.pub, "Please input a queue to publish warning"
    if arg.zmq:
        assert arg.sub, "Please input a queue to sub surrogate message"
    conn = boto.connect_sdb()
    t_domain = get_domain(conn, "s_holiday")

    if arg.zmq:
        with queue.open(arg.sub, 'r') as inq:
            for m in inq:
                try:
                    if arg.svm:
                        svm_warning(t_domain, m, arg.pub)
                    else:
                        warning_center(t_domain, m, arg.pub, float(arg.level))
                except KeyboardInterrupt:
                    log.info('GOT SIGINIT, exiting!')
                    break
                except:
                    log.exception("Exception in Process:%s" % sys.exc_info()[0])
    else:
        with open(arg.warn, "w") as w, open(arg.surr) as r:
            if arg.svm:
                for m in r:
                    m = json.loads(m)
                    warning = svm_warning(t_domain, m, arg.pub)
                    w.write(json.dumps(warning) + "\n")


if __name__ == "__main__":
    main()
