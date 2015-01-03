#!/usr/bin/env python
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

import logging
import os
import re
import subprocess

from resource_base import BuildTarget
from android_sqlite import AndroidSqlite

LOGGER = logging.getLogger(__name__)

def _new_fname(orig_fname, target_dir, new_ext=None):
    """Get the name with full path for the new media resource"""
    # No dash or uppercase forandroid resources
    fname = "ad"+re.sub("-", "_", os.path.basename(orig_fname)).lower()
    if new_ext:
        fname = os.path.splitext(fname)[0] + new_ext
    fname = os.path.join(target_dir, fname)
    return fname

class AndroidResourceTarget(BuildTarget):
    """Create resources for the android app"""
    def __init__(self, resource_dir=None):
        if not resource_dir:
            resource_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "android_assets"))
        super(AndroidResourceTarget, self).__init__(
            None, os.path.join(resource_dir, "sounds"),
            image_formats=set(["svg"]))

        resolutions = [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144),
                       ("xxxhdpi", 192)]

        self.image_destinations = [(os.path.join(resource_dir, "drawable-" + dpiname), dpi)
                                   for dpiname, dpi in resolutions]

        self.asset_dir = os.path.join(resource_dir, "assets")
        self.dbname = os.path.join(self.asset_dir, "exercises.db")

        for dname, _ in self.image_destinations + [(self.asset_dir, "foo")]:
            if not os.path.isdir(dname):
                os.makedirs(dname)

        self.media_callbacks["svg_processor"] = self.include_image

    def include_image(self, fname):
        """Create scaled bitmap versions of the svg images."""
        if not fname.endswith(".svg"):
            return
        with open(os.devnull, 'w') as fnull:
            for dname, dpi in self.image_destinations:
                new_fname = _new_fname(fname, dname, ".png")
                cmd = ["inkscape", "-z", "-f="+fname,
                       "--export-png="+new_fname, "-h=%d"%dpi]
                LOGGER.debug(" ".join(cmd))
                subprocess.call(cmd, stdout=fnull)

    def include_images(self, fnames):
        """Create scaled versions of the fixed assets."""
        for fname in fnames:
            self.include_image(fname)

    def write(self, index):
        """Write the resource files"""
        asq = AndroidSqlite(self.dbname)

        for lecture in index:
            for lang, ldoc in lecture["languages"].items():
                lec_key = asq.insert_lecture(lecture, ldoc, lang)
                for exer in lecture["Exercises"]:
                    exer_key = asq.insert_exercise(lec_key, lang, exer)
                    for alt in self._get_choices(exer):
                        asq.insert_choice(exer_key, exer["answer_type"], lang, alt)

    def clean_fname(self, fname):
        #FIXME
        return fname
