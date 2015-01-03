#!/usr/bin/env python3
"""Create the initial SQLite DB for android"""

import logging
import os
import sqlite3

LOGGER = logging.getLogger(__name__)

TABLE_CREATE_COMMANDS = [
    # Standard android tables
    """CREATE TABLE "android_metadata" ("locale" TEXT DEFAULT 'en_US')""",
    """INSERT INTO "android_metadata" VALUES ('en_US')""",

    # Lectures
    """CREATE TABLE "lectures" (
    _id INTEGER PRIMARY KEY,
    name TEXT,
    version VARCHAR(10),
    language VARCHAR(6),
    level INTEGER,
    link_name TEXT,
    link_url TEXT,
    instructions VARCHAR(2000)
    )""",

    # Exercises
    """CREATE TABLE "exercises" (
    _id INTEGER PRIMARY KEY,
    name TEXT,
    question_type TEXT,
    lecture INTEGER,
    question_sound TEXT,
    question_image TEXT,
    text TEXT)""",

    # Choice
    """CREATE TABLE "choices" (
    _id INTEGER PRIMARY KEY,
    answer_type TEXT,
    exercise INTEGER,
    correct BOOLEAN,
    sound TEXT,
    image TEXT,
    text TEXT
    )"""

]

class AndroidSqlite():
    """Create a sqlite database for the exercises"""
    # We could probably use Django object mapper to do this with less code

    def __init__(self, fname):
        if os.path.isfile(fname):
            os.unlink(fname)

        self.conn = sqlite3.connect(fname)
        cursor = self.conn.cursor()

        for tcc in TABLE_CREATE_COMMANDS:
            LOGGER.debug("Run sqllite: %s", tcc)
            cursor.execute(tcc)

        self.conn.commit()
        self.lecture_primary_key = 0
        self.exercise_primary_key = 0
        self.choice_primary_key = 0

    def __del__(self):
        """Close connection to make sure everything is written to db."""
        self.conn.close()

    def insert_lecture(self, doc, ldoc, lang):
        """Insert lecture info into db"""
        self.lecture_primary_key += 1
        cursor = self.conn.cursor()
        cmd = """INSERT INTO lectures VALUES(%d, "%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % (
            self.lecture_primary_key, ldoc["Title"], doc["Version"],
            lang, doc["Level"],
            ldoc["Outside_information"]["name"] if "Outside_information" in ldoc else "",
            ldoc["Outside_information"]["link"] if "Outside_information" in ldoc else "",
            ldoc["Instructions"] if "Instuctions" in ldoc else "")
        LOGGER.debug("%s", cmd)
        cursor.execute(cmd)
        self.conn.commit()
        return self.lecture_primary_key

    def insert_exercise(self, lec_key, lang, exer):
        """Insert exercise into db"""
        self.exercise_primary_key += 1
        cursor = self.conn.cursor()
        cmd = """INSERT INTO exercises VALUES (%d, "%s", "%s", %d, "%s", "%s", "%s")""" %(
            self.exercise_primary_key, exer["name"][lang],
            exer["question_type"], lec_key,
            exer["mp3"], exer["png"],
            exer["text"][lang] if "text" in exer and exer["text"] else "")
        LOGGER.debug("%s", cmd)
        cursor.execute(cmd)
        self.conn.commit()
        return self.exercise_primary_key

    def insert_choice(self, exer_key, answer_type, lang, alt):
        """Insert choice into db"""
        self.choice_primary_key += 1
        cursor = self.conn.cursor()
        cmd = """INSERT INTO choices VALUES """\
              """(%d, "%s", %d, %d, "%s", "%s", "%s")""" %(
                  self.choice_primary_key, answer_type,
                  exer_key, 1 if alt["correct"] else 0,
                  alt["mp3"], alt["png"],
                  alt["text"][lang] if "text" in alt and alt["text"] else "")
        LOGGER.debug("%s", cmd)
        cursor.execute(cmd)
        self.conn.commit()
        return self.choice_primary_key

