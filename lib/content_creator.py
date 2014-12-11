#!/usr/bin/env python
"""Creates the excercise contents."""

import copy
import itertools
import multiprocessing
import logging
import os
import random
import re
import subprocess
import sys
import yaml

from svgtransform import SvgTransform
from resource_simplehtml import SimpleHtmlTarget
from resource_django import PureDjangoTarget
from resource_android import AndroidResourceTarget

logger = logging.getLogger(__name__)

RANDOM_INSTRUMENTS = [
    "acoustic grand", "acoustic guitar (nylon)",
    "electric grand", "acoustic guitar (steel)", "harpsichord"]
#, "xylophone"]

TRANSPOSE_MAJOR = ["d", "e", "f", "g,", "a,", "bis,"]

NATURALIZE_TRANSPOSE_LY = """
#(define (naturalize-pitch p)
  (let ((o (ly:pitch-octave p))
        (a (* 4 (ly:pitch-alteration p)))
        ;; alteration, a, in quarter tone steps,
        ;; for historical reasons
        (n (ly:pitch-notename p)))
    (cond
     ((and (> a 1) (or (eq? n 6) (eq? n 2)))
      (set! a (- a 2))
      (set! n (+ n 1)))
     ((and (< a -1) (or (eq? n 0) (eq? n 3)))
      (set! a (+ a 2))
      (set! n (- n 1))))
    (cond
     ((> a 2) (set! a (- a 4)) (set! n (+ n 1)))
     ((< a -2) (set! a (+ a 4)) (set! n (- n 1))))
    (if (< n 0) (begin (set! o (- o 1)) (set! n (+ n 7))))
    (if (> n 6) (begin (set! o (+ o 1)) (set! n (- n 7))))
    (ly:make-pitch o n (/ a 4))))

#(define (naturalize music)
  (let ((es (ly:music-property music 'elements))
        (e (ly:music-property music 'element))
        (p (ly:music-property music 'pitch)))
    (if (pair? es)
       (ly:music-set-property!
         music 'elements
         (map (lambda (x) (naturalize x)) es)))
    (if (ly:music? e)
       (ly:music-set-property!
         music 'element
         (naturalize e)))
    (if (ly:pitch? p)
       (begin
         (set! p (naturalize-pitch p))
         (ly:music-set-property! music 'pitch p)))
    music))

naturalizeMusic =
#(define-music-function (parser location m)
  (ly:music?)
  (naturalize m))
"""

lilypond_template = r"""
\version "2.12.3"
\paper {
  indent = 0\mm
  line-width = 60\mm
  oddHeaderMarkup = ""
  evenHeaderMarkup = ""
  oddFooterMarkup = ##f
  evenFooterMarkup = ""
}
""" + NATURALIZE_TRANSPOSE_LY + r"""
\score {
  \new %s {
    \set Staff.midiInstrument = "%s"
  { %s } }
 \layout {}
 \midi {}
}
"""


class Content(object):
    """Parse the content definitions and create the associated files"""
    def __init__(self, target=PureDjangoTarget(), lecture=None, fname_list=None,
                 image_format="svg", host_type="macports", only_new=False,
                 lilypond_path=None, tmpdir=None):
        self.tmpdir = tmpdir if tmpdir\
          else os.path.join(os.path.dirname(__file__), "..", "work", "tmp")
        if not os.path.isdir(self.tmpdir):
            os.makedirs(self.tmpdir)

        self.image_format = image_format
        fname = None
        if not fname_list:
            dname = os.path.join(
                os.path.dirname(__file__),
                "..", "content", "lectures")
            fname_list = [f for f in os.listdir(dname) if f.endswith(".yaml")]
        self.index = []
        for fname in fname_list:
            with open(os.path.join(dname, fname), 'r') as ifh:
                self.index.append(yaml.load(ifh))

        if lecture:
            available_lectures = set([i["languages"]["en"]["Title"] for i in self.index])
            self.index = [i for i in self.index
                          if i["languages"]["en"]["Title"] == lecture]

            if not len(self.index):
                logger.critical(
                    "Lecture '%s' not found, choose one of %s", lecture,
                    sorted(available_lectures))
                sys.exit(-1)
            available_lectures = None # List not needed later

        for doc in self.index:
            if not "Exercises" in doc:
                doc["Exercises"] = []

        self.content_dir = os.path.dirname(fname)
        if host_type == "macports":
            self.binpath = "/opt/local/bin"
            self.timidity_path = self.binpath
            self.lilypond_path = self.binpath
            self.inkscape_path = self.binpath
        elif host_type == "linux":
            self.binpath = "/usr/bin"
            self.timidity_path = self.binpath
            self.lilypond_path = self.binpath
            self.inkscape_path = self.binpath
        if lilypond_path:
            self.lilypond_path = lilypond_path
        self.target = target
        self.only_new = only_new

        self.fixed_images = \
            [os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                          "content", "images", fname))
             for fname in ["empty_stave.png", "empty_stave.svg",
                           "logo.svg", "logo-white.svg", "logo-gray.svg",
                           "fi.png", "gb.png"]]


    def generate_extra_rounds(self):
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
                    if transpose:
                        if transpose == "random":
                            tstring = \
                                r"\naturalizeMusic \transpose c %s { " % (
                                    random.choice(TRANSPOSE_MAJOR))
                        else:
                            assert False
                    exer["notes"] = tstring + exer["notes"] + " }"
                    for alt in exer["confusers"]:
                        alt["notes"] = tstring + alt["notes"] +" }"
                doc["Exercises"].extend(tmp_exercises)

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
                contstr += "    Confusers: "
                contstr += ', '.join([repr(c["notes"]) for c in exer["confusers"]]) +"\n"
        return contstr

    @staticmethod
    def augment_missing_info(exer):
        """Fill in default values for the exercise, if missing"""
        if not "question_type" in exer or exer["question_type"] == "random":
            # Give audio question a 66% prob
            exer["question_type"], exer["answer_type"] = random.choice(
                [("image", "audio"), ("audio", "image"), ("audio", "image")])
            exer["generate_check"] = "random"

        if not "instrument" in exer or exer["instrument"] == "random":
            exer["instrument"] = random.choice(RANDOM_INSTRUMENTS)

        for conf in exer["confusers"]:
            if not "instrument" in conf:
                conf["instrument"] = exer["instrument"]
            if not "tempo" in conf and "tempo" in exer:
                conf["tempo"] = exer["tempo"]
            if not "hidden_tempo" in conf and "hidden_tempo" in exer:
                conf["hidden_tempo"] = exer["hidden_tempo"]
            if "style" in exer:
                conf["style"] = exer["style"]

    def expand_alternative_questions(self):
        """Generate different permutations of a question if requested"""
        def replace_media(orig, new):
            """Replace media info in orig with the info in new"""
            orig["notes"] = new["notes"]
            orig["image"] = new["image"]
            orig["ogg"] = new["ogg"]
            orig["mp3"] = new["mp3"]
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

    def create_lilypond_file(self, conv, fname):
        """Create the source lilypond notation"""
        body = ""
        if "tempo" in conv:
            body += r"\tempo 4 = %d" % conv["tempo"]
        if "hidden_tempo" in conv:
            body += r"\set Score.tempoHideNote = ##t "\
              r"\tempo 4 = %d " % conv["hidden_tempo"]

        if "style" in conv:
            style = conv["style"]
            if style == "chord":
                body += r"\key c \major << { \chordmode { " +\
                   conv["notes"] + " } } "
            if style == "interval" or style == "scale":
                body += r" \key c \major << { " +\
                   conv["notes"] + " } "

            if style == "chord" or style == "interval" or style == "scale":
                if "annotation" in conv:
                    body += r"\addlyrics { " + conv["annotation"] + " }"
                body += " >>"

            if style == "drums":
                body += r"{ \drummode { " + conv["notes"] + "} }"
                staffstring = "DrumStaff"
            else:
                staffstring = "Staff"

        else:
            body += conv["notes"]
            staffstring = "Staff"
        with open(fname, "w") as lyfh:
            lyfh.write(lilypond_template % (
                staffstring, conv["instrument"], body))

    def create_staff_image(self, conv, input_fname, tmpfname):
        """Create the image and corresponding midi file from lilypond source."""
        with open(os.devnull, 'w') as fnull:
            if self.image_format == "png": # Generate png images
                cmd = "%s/lilypond --png -dpixmap-format=pngalpha %s" % (
                    self.lilypond_path, os.path.basename(input_fname))
                if subprocess.call(cmd.split(), cwd=self.tmpdir,
                                   stdout=fnull, stderr=fnull):
                    raise RuntimeError("Failed '%s'" % cmd)
                cmd = "%s/convert %s -trim %s" % (
                    self.binpath, tmpfname, conv["image"])
                if subprocess.call(
                        cmd.split(),
                        stdout=fnull, stderr=fnull):
                    raise RuntimeError("Failed '%s'" % cmd)
                return

            if self.image_format == "svg": # Generate svg images
                cmd = "%s/lilypond -dbackend=svg %s" % (
                    self.lilypond_path, os.path.basename(input_fname))

                if subprocess.call(cmd.split(), cwd=self.tmpdir,
                                   stdout=fnull, stderr=fnull):
                    raise RuntimeError("Failed '%s'" % cmd)
                strans = SvgTransform.init_from_file(tmpfname, self.inkscape_path)
                strans.crop()
                strans.write(conv["image"])
                return

        assert False

    def create_sounds(self, conv, input_fname):
        """Create sounds from the midi file."""
        soxbase = ["%s/sox" % self.binpath, "-t", "raw", "-r", "44100",
                   "-b", "24", "-e", "signed-integer", "-c", "1", "-"]
        timidity_base = ["%s/timidity" % self.timidity_path, input_fname,
                         "-Or2slM", "-o", "-", "-s", "44100 ",
                         "--volume-compensation"]

        with open(os.devnull, 'w') as fnull:
            for audio_format in ["mp3", "ogg"]:
                timidityp = subprocess.Popen(
                    timidity_base, stdout=subprocess.PIPE, stderr=fnull)
                soxp = subprocess.Popen(soxbase + [conv[audio_format]],
                                        stdin=timidityp.stdout)
                soxp.communicate()
                timidityp.communicate()
                if timidityp.returncode:
                    raise RuntimeError("Failed timidity '%s'" %
                                       " ".join(timidity_base))
                if soxp.returncode:
                    raise RuntimeError("Failed sox '%s'" %
                                       " ".join(soxbase + [conv[audio_format]]))

    def compile(self, max_processes=8):
        """Create all media."""
        self.generate_extra_rounds()

        media_list = []
        for doc in self.index:
            to_png = []
            for exer in doc["Exercises"]:
                self.augment_missing_info(exer)
                to_png.extend([exer] + exer["confusers"])

            for i, conv in enumerate(to_png):
                title = doc["languages"]["en"]["Title"]
                logstring = "%s #%d" % (title, i+1)
                title_us = re.sub(r"\s", "_", doc["languages"]["en"]["Title"])
                fname_base = "%s-%d" % (title_us, i)

                conv["image"] = os.path.join(
                    self.target.image_dir, fname_base+ "." + self.image_format)
                conv["mp3"] = os.path.join(
                    self.target.sound_dir, fname_base + ".mp3")
                conv["ogg"] = os.path.join(
                    self.target.sound_dir, fname_base + ".ogg")

                lytmp = os.path.join(
                    self.tmpdir, fname_base + ".ly")
                imagetmp = os.path.join(
                    self.tmpdir, fname_base + "." + self.image_format)
                miditmp = os.path.join(
                    self.tmpdir, fname_base + ".midi")

                if not (self.only_new and os.path.isfile(conv["image"])
                        and os.path.isfile(conv["mp3"]) and
                        os.path.isfile(conv["mp3"])):
                    media_list.append([self, logstring, conv,
                                       lytmp, imagetmp, miditmp])

        pool = multiprocessing.Pool(processes=max_processes)
        pool.map(poolwrap_create_media, media_list)

        self.target.include_fixed_images(self.fixed_images)
        self.expand_alternative_questions()
        self.target.write(self.index)

    def create_media(self, logstring, conv, lytmp, imagetmp, miditmp):
        """Create the actual media files"""
        logger.info(logstring)
        self.create_lilypond_file(conv, lytmp)
        self.create_staff_image(conv, lytmp, imagetmp)
        self.create_sounds(conv, miditmp)

def poolwrap_create_media(argtuple):
    """A wrapper for media creation since multiprocessing.Pool
    cannot handle in-class functions."""
    cinstance, conv, logstring, lytmp, imgtmp, miditmp = argtuple
    cinstance.create_media(conv, logstring, lytmp, imgtmp, miditmp)
    return True


def main():
    """Create content"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Creates content for music training.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    target_choices = ["puredjango", "simple_html", "android"]
    host_types = ["macports", "linux"]
    image_formats = ["png", "svg"]

    parser.add_argument("-t", "--target",
                        help="Generate content for which format. "\
                          "Options: " + repr(target_choices) +".",
                        choices=target_choices,
                        default=target_choices[0])
    parser.add_argument("-l", "--lecture",
                        help="Generate content only for LECTURE",
                        metavar="LECTURE", default=None)
    parser.add_argument("-n", "--only_new", action="store_true",
                        help="Generate files only for missing stuff.")
    parser.add_argument("-H", "--host_type", choices=host_types,
                        default=host_types[0],
                        help="Host type for setting the paths to binaries. "\
                          "Options: " + repr(host_types) + ".")
    parser.add_argument("-i", "--image_format", choices=image_formats,
                        default=image_formats[0],
                        help="Image output format. "\
                          "Options: " + repr(host_types) + ".")
    parser.add_argument("-L", "--lilypond_path", metavar="path",
                        help="Lilypond executable path",
                        default=None)
    parser.add_argument('-v', '--verbose', dest="verbose", type=int,
                        default=1, metavar='<int>',
                        help="verbose level (default %(default)s)")

    args = parser.parse_args()

    if args.verbose >= 2:
        loglevel = logging.DEBUG
    elif args.verbose >= 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING
    logging.basicConfig(format='%(module)s: %(message)s',
                        level=loglevel)

    if args.target == "puredjango":
        target = PureDjangoTarget()
    elif args.target == "simple_html":
        target = SimpleHtmlTarget()
    elif args.target == "android":
        target = AndroidResourceTarget()

    content = Content(
        target, lecture=args.lecture, only_new=args.only_new,
        host_type=args.host_type, lilypond_path=args.lilypond_path,
        image_format=args.image_format)
    content.compile()

