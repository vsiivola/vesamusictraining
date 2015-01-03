#!/usr/bin/env python
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

import logging
import os
import re

from resource_base import BuildTarget

LOGGER = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0
Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en-US" xml:lang="en-US" xmlns="http://www.w3.org/1999/xhtml">
<head>
</head>
<body>
%s
</body>"""

class SimpleHtmlTarget(BuildTarget):
    """Create simple raw html pages for debugging."""

    def __init__(self, htmlfile=None, mediadir=None):
        basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simple_html"))
        self.htmlfile = htmlfile if htmlfile else\
          os.path.join(basedir, "index.html")
        mediadir = mediadir if mediadir else\
          os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simple_html", "media"))
        super(SimpleHtmlTarget, self).__init__(
            mediadir, mediadir, sound_formats=set(["mp3", "ogg"]))

    @staticmethod
    def clean_fname(fname):
        """Fix the file names to be relative to the index.html"""
        return re.sub('^.*simple_html/', '', fname)

    def write(self, content_index):
        """Write the web pages and the corresponding media"""

        def image_str(fname):
            """HTML string for showing the image"""
            return '<img src="%s"></img>' % fname

        def audio_str(oggname, mp3name):
            """HTML string for playing the audio"""
            return """<audio controls="controls">
<source src="%s" type="audio/ogg" />
<source src="%s" type="audio/mpeg" />
<a href="%s">Play</a></audio>""" % (oggname, mp3name, mp3name)

        pagestr = ""
        pagestr += "<h2>Musical Notation Trainer</h2>\n"
        pagestr += "<ul>\n"
        for doc in content_index:
            pagestr += "<li>%s (%d exercises)</li>\n" % (
                doc["languages"]["en"]["Title"], len(doc["Exercises"]))
        pagestr += "</ul>\n"
        pagestr += "</p>\n\n"

        for doc in [doc2 for doc2 in content_index if len(doc2["Exercises"]) > 0]:
            pagestr += "<h2>%s</h2>\n" % doc["languages"]["en"]["Title"]
            for exer in doc["Exercises"]:
                pagestr += "<h3>%s</h3>\n" % exer["name"]["en"].capitalize()
                pagestr += '<table cellpadding="10" border="1">\n'
                pagestr += '<tr><td colspan="3" align="center">'
                if exer["question_type"] == "audio":
                    pagestr += audio_str(exer["ogg"], exer["mp3"])
                else:
                    pagestr += image_str(exer["png"])
                pagestr += "</td></tr>\n"
                alternatives = []
                for alt in [exer] + exer["confusers"]:
                    text = alt["text"]["en"] \
                      if "text" in alt and alt["text"] else None
                    if exer["answer_type"] == "image":
                        alternatives.append(
                            (image_str(alt["png"]),
                             audio_str(alt["ogg"], alt["mp3"]), text))
                    elif exer["answer_type"] == "audio":
                        alternatives.append(
                            (audio_str(alt["ogg"], alt["mp3"]),
                             image_str(alt["png"]), text))
                pagestr += "<tr>\n"

                # FIXME: randomize order
                pagestr += '<td align="center">' + '</td>\n<td align="center">'.join(
                    [atmp[0] for atmp in alternatives])+"</td>"
                pagestr += "</tr>\n"
                if any([atmp[2] for atmp in alternatives]):
                    pagestr += "<tr>\n"
                    pagestr += '<td align="center">' + \
                         '</td>\n<td align="center">'.join(
                             [atmp[2] for atmp in alternatives])+"</td>"
                    pagestr += "</tr>\n"


                pagestr += "<tr>\n"
                pagestr += '<td align="center">' + '</td>\n<td align="center">'.join(
                    [atmp[1] for atmp in alternatives])+"</td>"
                pagestr += "</tr>\n"
                pagestr += "</table></p>\n"

        with open(self.htmlfile, "w") as ofh:
            ofh.write(HTML_TEMPLATE % pagestr)
