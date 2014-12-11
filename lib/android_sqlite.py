#!/usr/bin/env python3
"""Create the initial SQLite DB for android"""

import logging
import os
import sqlite3


LOGGER = logging.getLogger(__name__)

class AndroidSqlite():
    """Create a sqlite database for the exercises"""
    # We could probably use Django object mapper to do this with less code

    def __init__(self, fname):
        if os.path.isfile(fname):
            os.unlink(fname)

        self.conn = sqlite3.connect(fname)
        cursor = self.conn.cursor()

        cmd = """CREATE TABLE "android_metadata" ("locale" TEXT DEFAULT 'en_US')"""
        cursor.execute(cmd)

        cmd = """INSERT INTO "android_metadata" VALUES ('en_US')"""
        cursor.execute(cmd)

        cmd = """CREATE TABLE "lectures" (_id INTEGER PRIMARY KEY, name TEXT)"""
        cursor.execute(cmd)

        self.conn.commit()

        self.lecture_primary_key = 1;

    def __del__(self):
        """Close connection to make sure everything is written to db."""
        self.conn.close()

    def insert_lecture(self, lecture):
        """Insert lecture info into db"""
        cursor = self.conn.cursor()

        for lang, ldoc in lecture["languages"].items():
            if lang != "en":
                continue
            cmd = """INSERT INTO lectures VALUES(%d, "%s")""" % (
                self.lecture_primary_key, ldoc["Title"])
            self.lecture_primary_key += 1
            LOGGER.debug("IC: %s", cmd)
            cursor.execute(cmd)

        self.conn.commit()


