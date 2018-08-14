#!/usr/bin/env python
"""Defines, how the base content created by content_creator should be
modified and stored for the given target. This base class defines
the interfaces, actual implementation is in the child classes.
"""

import logging
import os
import random
import shutil
import uuid
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from lilypond_source import LilyCompileTask, LilySource

LOGGER = logging.getLogger(__name__)

class BuildTarget():
    """Defines a basic function class for creating the media
    and database files. Should be inherited from."""
    def __init__(self, image_dir: Optional[str] = None,
                 sound_dir: Optional[str] = None,
                 tmp_dir: Optional[str] = None,
                 image_formats: Set[str] = set(["png"]),
                 sound_formats: Set[str] = set(["mp3"])) -> None:
        self.image_dir = image_dir if image_dir \
          else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "work", "png"))
        self.sound_dir = sound_dir if sound_dir\
          else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "work", "mp3"))
        self.tmp_dir = tmp_dir if tmp_dir\
          else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "work", "tmp"))

        if not os.path.isdir(self.image_dir):
            os.makedirs(self.image_dir)
        if not os.path.isdir(self.sound_dir):
            os.makedirs(self.sound_dir)
        if not os.path.isdir(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        self.image_formats = image_formats
        self.sound_formats = sound_formats

        self.media_callbacks: Dict[str, Callable[[str], None]] = dict()

    def media_compile_tasklist(self, lysrc_list: List[LilySource]) -> Tuple[Dict, Dict]:
        """Create a list of media compile tasks"""
        unique_sounds = dict()
        unique_images = dict()

        # Get dicts only none lysrc per signature
        # We do not need to care about overwrite to the dict,
        # any of the similar signature items would do
        for lysrc in lysrc_list:
            unique_sounds[lysrc.sound_signature()] = lysrc
            unique_images[lysrc.image_signature()] = lysrc

        # Create media compile tasks for unique outputs
        sound_tasks = dict()
        for sound_signature, lysrc in unique_sounds.items():
            id_str = str(uuid.uuid4())
            lyfname = os.path.join(self.tmp_dir, id_str+".ly")
            with open(lyfname, "w") as lyout:
                lyout.write(lysrc.__str__())

            lct = LilyCompileTask(lyfname, self.sound_formats,
                                  os.path.join(self.tmp_dir, id_str),
                                  os.path.join(self.sound_dir, id_str))
            sound_tasks[sound_signature] = lct
            #LOGGER.debug(lct)

        image_tasks = dict()
        for image_signature, lysrc in unique_images.items():
            id_str = str(uuid.uuid4())
            lyfname = os.path.join(self.tmp_dir, id_str+".ly")
            with open(lyfname, "w") as lyout:
                lyout.write(lysrc.__str__())

            lct = LilyCompileTask(lyfname, self.image_formats,
                                  os.path.join(self.tmp_dir, id_str),
                                  os.path.join(self.image_dir, id_str))

            image_tasks[image_signature] = lct
            #LOGGER.debug(lct)

        return sound_tasks, image_tasks

    def include_images(self, orig_images: Iterable[str]) -> None:
        """Default copy for static image files."""
        for fname in orig_images:
            shutil.copy(fname, self.image_dir)

    def write(self, _) -> None:
        """Stub for writing out any DBs or fictures. Must be implemented
        by the child."""
        pass

    @staticmethod
    def _get_choices(exer: Dict, shuffle: bool = True) -> List:
        """Return a list that contains both correct and incorrect choices"""

        # Mark which one is correct and which are false
        exer["correct"] = True
        for cexer in exer["confusers"]:
            cexer["correct"] = False

        alts = [exer] + exer["confusers"]
        if shuffle:
            random.shuffle(alts)
        return alts

    def clean_fname(self, fname: str) -> str:
        """Stub for modifying the filenames according to the target."""
        return fname
