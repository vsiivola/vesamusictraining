#!/usr/bin/env python
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

import logging
import os
import re
import subprocess
import sys

from resource_base import BuildTarget

logger = logging.getLogger(__name__)

class AndroidResourceTarget(BuildTarget):
    """Create resources for the android app"""
    def __init__(self, asset_dir=None):
        if not asset_dir:
            asset_dir = os.path.join(
                os.path.dirname(__file__),
                "..", "android_assets", "res")
        super(AndroidResourceTarget, self).__init__(None, None, None)

        resolutions = [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144),
                       ("xxxhdpi", 192)]

        self.image_destinations = [(os.path.join(asset_dir, "drawable-" + dpiname), dpi)
                                   for dpiname, dpi in resolutions]

        for dname, _ in self.image_destinations:
            if not os.path.isdir(dname):
                os.makedirs(dname)

    def include_fixed_images(self, fnames):
        """Create scaled versions of the fixed assets."""
        for fname in fnames:
            if not fname.endswith(".svg"):
                logger.debug("Skipping fixed image %s", fname)
                continue
            for dname, dpi in self.image_destinations:
                new_fname = os.path.join(
                    dname,
                    re.sub("-", "_", os.path.splitext(os.path.basename(fname))[0]) + ".png")
                cmd = ["inkscape", "-z", "-f="+fname,
                       "--export-png="+new_fname, "-h=%d"%dpi]
                logger.info(" ".join(cmd))
                subprocess.call(cmd)

    def write(self, index):
        """Write the resource files"""

        for doc in index:
            for exercise in doc["Exercises"]:
                logger.info("excercise %s", repr(exercise))
                sys.exit(-1)

        # Convert images to different resolution pixmaps
