#!/usr/bin/env python
"""Defines, how the base content created by content_creator should be
modified and stored for the given target. This base class defines
the interfaces, actual implementation is in the child classes.
"""

#import logging
import os
import random
import shutil

#LOGGER = logging.getLogger(__name__)

class BuildTarget(object):
    """Defines a basic function class for creating the media
    and database files. Should be inherited from."""
    def __init__(self, yaml_fname="generated_course.yaml",
                 image_dir=None, sound_dir=None):
        self.image_dir = image_dir if image_dir \
          else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "work", "png"))
        self.sound_dir = sound_dir if sound_dir\
          else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "work", "mp3"))
        self.yaml_fname = yaml_fname

        if not os.path.isdir(self.image_dir):
            os.makedirs(self.image_dir)
        if not os.path.isdir(self.sound_dir):
            os.makedirs(self.sound_dir)

        if self.yaml_fname:
            yaml_dir = os.path.dirname(self.yaml_fname)
            if not os.path.isdir(yaml_dir):
                os.makedirs(yaml_dir)

    def include_images(self, orig_images):
        """Default copy for static image files."""
        for fname in orig_images:
            shutil.copy(fname, self.image_dir)

    def write(self, _):
        """Stub for writing out any DBs or fictures. Must be implemented
        by the child."""
        pass

    @staticmethod
    def _get_choices(exer, shuffle=True):
        """Return a list that contains both correct and incorrect choices"""

        # Mark which one is correct and which are false
        exer["correct"] = True
        for cexer in exer["confusers"]:
            cexer["correct"] = False

        alts = [exer] + exer["confusers"]
        if shuffle:
            random.shuffle(alts)
        return alts


