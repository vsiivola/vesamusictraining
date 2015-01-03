#!/usr/bin/env python
"""Creates the excercise outline."""

import copy
import itertools
import logging
import os
import random
import re
import yaml

from lilypond_source import get_random_transpose_key, LilySource

LOGGER = logging.getLogger(__name__)

class ContentException(Exception):
    """Exception in handling content YAML files"""
    pass

class Content(object):
    """Parse the content definitions."""
    def __init__(self, lectures=None, fname_list=None):
        if not fname_list:
            # No lectures spesified, find all in default dir
            dname = os.path.join(
                os.path.dirname(__file__),
                "..", "content", "lectures")
            fname_list = [f for f in os.listdir(dname) if f.endswith(".yaml")]

        self.index = []
        for fname in fname_list:
            with open(os.path.join(dname, fname), 'r') as ifh:
                self.index.append(yaml.load(ifh))

        if lectures:
            available_lectures = set([i["languages"]["en"]["Title"] for i in self.index])
            self.index = [i for i in self.index
                          if i["languages"]["en"]["Title"] in lectures]

            if not len(self.index):
                LOGGER.critical(
                    "Lecture '%s' not found, choose one of %s", lectures,
                    sorted(available_lectures))
                raise ContentException("Unknown lecture")
            available_lectures = None # List not needed later

        for doc in self.index:
            if not "Exercises" in doc:
                doc["Exercises"] = []

        self._convert_to_lilysource()

        self.fixed_images = \
            [os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                          "content", "images", fname))
             for fname in ["empty_stave.png", "empty_stave.svg",
                           "logo.svg", "logo-white.svg", "logo-gray.svg",
                           "fi.png", "gb.png"]]

    def content2string(self):
        """Get a string representation of the content"""
        contstr = ""
        for doc in self.index:
            exercises = doc["Exercises"]
            contstr += "%s (%d exercises)\n" % (
                doc["languages"]["en"]["Title"], len(exercises))
            for exer in exercises:
                contstr += "  %s: question type '%s', answer type '%s'\n" % (
                    exer["name"],
                    exer["question_type"] if "question_type" in exer else "random",
                    exer["answer_type"] if "answer_type" in exer else "random")
                contstr += "    Reference: '%s'\n" % exer["notes"]
                contstr += "    Transpose: '%s'\n" % exer["transpose"] \
                           if "transpose" in exer else "None"
                contstr += "    Confusers: "
                contstr += ', '.join([repr(c["notes"]) for c in exer["confusers"]]) +"\n"
        return contstr

    def _generate_extra_rounds(self):
        """Generate the transposed extra exercises if requested"""
        for doc in self.index:
            if "Rounds" in doc:
                if doc["Rounds"][0] != "normal":
                    exercise_template = copy.deepcopy(doc["Exercises"])
                    roundskip = 0
                else:
                    exercise_template = doc["Exercises"]
                    roundskip = 1
            else:
                doc["Rounds"] = ["normal"]
                roundskip = 1

            for eround in doc["Rounds"][roundskip:]:
                tmp_exercises = copy.deepcopy(exercise_template)
                if eround == "transpose random":
                    transpose = "random"
                else:
                    transpose = False

                for exer in tmp_exercises:
                    if transpose == "random":
                        transpose_key = get_random_transpose_key()
                        exer["transpose"] = transpose_key
                        for alt in exer["confusers"]:
                            alt["transpose"] = transpose_key
                    elif transpose: # Unknown transpose type
                        assert False

                doc["Exercises"].extend(tmp_exercises)

    @staticmethod
    def _augment_missing_info(exer):
        """Fill in default values for the exercise, if missing"""
        if not "question_type" in exer or exer["question_type"] == "random":
            # Give audio question a 66% prob
            exer["question_type"], exer["answer_type"] = random.choice(
                [("image", "audio"), ("audio", "image"), ("audio", "image")])
            exer["generate_check"] = "random"

        for conf in exer["confusers"]:
            if not conf["lysrc"].tempo:
                conf["lysrc"].tempo = exer["lysrc"].tempo
            if not conf["lysrc"].hidden_tempo:
                conf["lysrc"].hidden_tempo = exer["lysrc"].hidden_tempo
            conf["lysrc"].style = exer["lysrc"].style
            #if not conf["lysrc"].instrument:
            conf["lysrc"].instrument = exer["lysrc"].instrument

    def _expand_alternative_questions(self):
        """Generate different permutations of a question if requested"""
        def replace_media(orig, new):
            """Replace media info in orig with the info in new"""
            orig["lysrc"].notes = new["lysrc"].notes
            orig["text"] = new["text"] if "text" in new else None

        for doc in self.index:
            tmp_exercises = doc["Exercises"]
            doc["Exercises"] = []
            for exer in tmp_exercises:
                if not "generate" in exer or exer["generate"] == "single":
                    doc["Exercises"].append(exer)
                    continue

                all_alts = [exer] + exer["confusers"]
                match = re.match(r'(\d+) first', exer["generate"])
                if match:
                    range_limit = int(match.group(1))
                else:
                    range_limit = len(all_alts)

                randomize_type = "generate_check" in exer and \
                  exer["generate_check"] == "random"
                permutations = [exer]

                for i in range(1, range_limit):
                    e_tmp = copy.deepcopy(exer)
                    if randomize_type:
                        e_tmp["question_type"], e_tmp["answer_type"] = \
                          random.choice(
                              [("image", "audio"),
                               ("audio", "image"),
                               ("audio", "image")])

                    main_choice = all_alts[i]
                    others = random.choice(list(itertools.permutations(
                        [all_alts[i2]
                         for i2 in range(0, len(all_alts)) if i != i2])))
                    replace_media(e_tmp, main_choice)
                    for idx2 in range(0, len(others)):
                        replace_media(e_tmp["confusers"][idx2], others[idx2])
                    permutations.append(e_tmp)

                random.shuffle(permutations)
                for i, perm in enumerate(permutations):
                    for lang in perm["name"].keys():
                        perm["name"][lang] += " %d" % (i+1)
                    doc["Exercises"].append(perm)

    def expand(self):
        """Create all exercise rounds (repeats, transposes)."""
        self._generate_extra_rounds()
        for doc in self.index:
            for exer in doc["Exercises"]:
                self._augment_missing_info(exer)
        self._expand_alternative_questions()

    def _convert_to_lilysource(self):
        """Put the info needed for lilypond creation to LilySource object."""
        ly_var_keys = ["notes", "annotation", "tempo", "hidden_tempo",
                       "style", "instrument", "transpose"]

        for eresp in self.get_questions_and_choices():
            # Ensure all vals exist
            for ly_var in ly_var_keys:
                if not ly_var in eresp:
                    eresp[ly_var] = None

            # Create the lysrc object
            eresp["lysrc"] = LilySource(eresp["notes"], eresp["annotation"], eresp["tempo"],
                                        eresp["hidden_tempo"], eresp["style"],
                                        eresp["instrument"], eresp["transpose"])

            # No need to keep the ly_var info around elsewhere
            for ly_var in ly_var_keys:
                del eresp[ly_var]

    def get_questions_and_choices(self):
        """List all items that need media resources"""
        for doc in self.index:
            for exer in doc["Exercises"]:
                yield exer
                for alt in exer["confusers"]:
                    yield alt

    def insert_filenames(self, sound_tasks, image_tasks):
        """Insert deduplicated media fnames into the lecture index."""
        for eresp in self.get_questions_and_choices():
            LOGGER.debug("Initial %s", eresp)
            lysrc = eresp["lysrc"]
            ssign = lysrc.sound_signature()

            if ssign in sound_tasks:
                LOGGER.debug("Found ssign")
                ly_task = sound_tasks[ssign]
                eresp["mp3"] = ly_task.mp3_fname
                eresp["ogg"] = ly_task.ogg_fname

            isign = lysrc.image_signature()
            if isign in image_tasks:
                LOGGER.debug("Found isign")
                ly_task = image_tasks[isign]
                eresp["png"] = ly_task.png_fname
                eresp["svg"] = ly_task.svg_fname
            LOGGER.debug("After %s", eresp)
