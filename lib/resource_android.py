#!/usr/bin/env python
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

import logging
import os
import re
import subprocess
import shutil
import sys

from resource_base import BuildTarget
from android_sqlite import AndroidSqlite

LOGGER = logging.getLogger(__name__)

def _new_fname(orig_fname, target_dir, new_ext=None):
    """Get the name with full path for the new media resource"""
    fname = os.path.basename(re.sub("-", "_", orig_fname)) # No dash for android resources
    if new_ext:
        fname = os.path.splitext(fname)[0] + new_ext
    fname = os.path.join(target_dir, fname)
    return fname

class AndroidResourceTarget(BuildTarget):
    """Create resources for the android app"""
    def __init__(self, asset_dir=None):
        if not asset_dir:
            asset_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "android_assets", "res"))
        super(AndroidResourceTarget, self).__init__(
            None, None, os.path.join(asset_dir, "sounds"))

        resolutions = [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144),
                       ("xxxhdpi", 192)]

        self.image_destinations = [(os.path.join(asset_dir, "drawable-" + dpiname), dpi)
                                   for dpiname, dpi in resolutions]

        for dname, _ in self.image_destinations:
            if not os.path.isdir(dname):
                os.makedirs(dname)

        self.dbname = os.path.join(asset_dir, "exercises.db")

    def include_images(self, fnames):
        """Create scaled versions of the fixed assets."""
        for fname in fnames:
            if not fname.endswith(".svg"):
                LOGGER.debug("Skipping fixed image %s", fname)
                continue
            for dname, dpi in self.image_destinations:
                new_fname = _new_fname(fname, dname, ".png")
                cmd = ["inkscape", "-z", "-f="+fname,
                       "--export-png="+new_fname, "-h=%d"%dpi]
                LOGGER.debug(" ".join(cmd))
                subprocess.call(cmd)

    def write(self, index):
        """Write the resource files"""
        asq = AndroidSqlite(self.dbname)

        for doc in index:
            asq.insert_lecture(doc)

            for exer in doc["Exercises"]:
                #LOGGER.debug("excercise %s", repr(exer))
                for alt in self._get_choices(exer):
                    self.include_images([alt["image"]])
                    sound = alt["ogg"]
                    shutil.copy(sound, _new_fname(sound, self.sound_dir))
