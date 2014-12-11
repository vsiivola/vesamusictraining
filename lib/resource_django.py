#!/usr/bin/env python
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

#import logging
import os
import random
import re
import yaml

from resource_base import BuildTarget

#LOGGER = logging.getLogger(__name__)

class PureDjangoTarget(BuildTarget):
    """Create media and corresponding Django db fixtures"""
    def __init__(self, media_target_dir=None, fixture_target=None):
        """Arguments:
        media_target_dir: Where to put the generated media assets
        fixture_target_dir: Where to put the Django db init fixtures.
        """
        if not media_target_dir:
            self.media_target_dir = os.path.join(
                os.path.dirname(__file__), "..", "vesamusictraining",
                "static", "generated_assets")

        if not fixture_target:
            fixture_target = os.path.join(
                os.path.dirname(__file__), "..", "vesamusictraining",
                "exercise", "fixtures", "initial_data.yaml")

        super(PureDjangoTarget, self).__init__(
            fixture_target,
            os.path.join(self.media_target_dir, "images"),
            os.path.join(self.media_target_dir, "sounds"))

    def write(self, index):
        """Write the fixtures"""
        if self.yaml_fname:
            with open(self.yaml_fname, "w") as ofh:
                ofh.write(yaml.dump(self._fixturize(index)))

    def _fixturize(self, index, lang="fi"):
        """Convert the human readable course definitions to Django fixtures"""
        def clean_fname(fname):
            """Modify the filenames for the web server"""
            # FIXME: hardcoded path
            return re.sub(
                self.media_target_dir, "/static/generated_assets", fname)

        fixtures = []
        eidx = 0
        cidx = 0
        lidx = 0

        for doc in index:
            for lang, ldoc in doc["languages"].items():
                fields_dict = {
                    "title" : ldoc["Title"],
                    "version" : doc["Version"],
                    "language": lang,
                    "level": doc["Level"]
                }
                if "Outside_information" in ldoc:
                    oinfo = ldoc["Outside_information"]
                    assert "name" in oinfo and "link" in oinfo
                    fields_dict["outside_info_name"] = oinfo["name"]
                    fields_dict["outside_info_link"] = oinfo["link"]

                if "Instructions" in ldoc:
                    fields_dict["instructions"] = ldoc["Instructions"]


                fixtures.append({"model": "exercise.Lecture",
                                 "pk": lidx,
                                 "fields": fields_dict})

                for exer in doc["Exercises"]:
                    exer["correct"] = True
                    for cexer in exer["confusers"]:
                        cexer["correct"] = False

                    alts = [exer] + exer["confusers"]
                    random.shuffle(alts)

                    fixtures.append({
                        "model": "exercise.Exercise",
                        "pk": eidx,
                        "fields": {
                            "title": exer["name"][lang],
                            "question_type": exer["question_type"],
                            "lecture": lidx,
                            "question_mp3": clean_fname(exer["mp3"]),
                            "question_ogg": clean_fname(exer["ogg"]),
                            "question_image": clean_fname(exer["image"]),
                            "text": exer["text"][lang] if \
                              "text" in exer and exer["text"] else ""
                        }})

                    for alt in alts:
                        fixtures.append({
                            "model" : "exercise.Choice",
                            "pk" : cidx,
                            "fields": {
                                "answer_type": exer["answer_type"],
                                "exercise": eidx,
                                "correct": alt["correct"],
                                "image": clean_fname(alt["image"]),
                                "ogg": clean_fname(alt["ogg"]),
                                "mp3": clean_fname(alt["mp3"]),
                                "text": alt["text"][lang] if \
                                "text" in alt and alt["text"] else ""}})
                        cidx += 1
                    eidx += 1
                lidx += 1
        return fixtures



