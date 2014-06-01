#!/usr/bin/env python
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

import copy
import itertools
import os
import random
import re
import shutil
import subprocess
import sys
import yaml

from SvgTransform import SvgTransform

class BuildTarget(object):
    """Defines a basic function class for creating the media
    and database files. Should be inherited from."""
    def __init__(self, yaml_fname="generated_course.yaml", pngdir="png",
                 mp3dir="mp3", workdir="work"):
        self.pngdir = pngdir
        self.mp3dir = mp3dir
        self.workdir = workdir
        self.yaml_fname = yaml_fname

        try:
            os.mkdir(self.pngdir)
        except OSError:
            pass
        try:
            os.mkdir(self.mp3dir)
        except OSError:
            pass
        try:
            os.mkdir(self.workdir)
        except OSError:
            pass

    def copy_files(self):
        """Make the static media files available."""
        for f in ["empty_stave.png", "logo.svg", "fi.png", "gb.png"]:
            shutil.copy(os.path.join("content", f), self.pngdir)

class PureDjangoTarget(BuildTarget):
    """Create media and corresponding Django db fixtures"""
    def __init__(self, media_target_dir=None, fixture_target_dir=None):
        """Arguments:
        media_target_dir: Where to put the generated media assets
        fixture_target_dir: Where to put the Django db init fixtures.
        """
        if not media_target_dir:
            self.media_target_dir = os.path.join(
                os.path.dirname(__file__), "..", "vesamusictraining",
                "static", "generated_assets")
        try:
            sound_dir = os.path.join(self.media_target_dir, "sounds")
            image_dir = os.path.join(self.media_target_dir, "images")
            os.makedirs(sound_dir)
            os.makedirs(image_dir)
        except OSError:
            pass

        if not fixture_target_dir:
            fixture_dir = os.path.join(
                os.path.dirname(__file__), "..", "vesamusictraining",
                "exercise", "fixtures")
        try:
            os.mkdir(fixture_dir)
        except OSError:
            pass

        super(PureDjangoTarget, self).__init__(
            os.path.join(fixture_dir, "initial_data.yaml"),
            image_dir, sound_dir)

    def write(self, index):
        """Write the fixtures"""
        ofh = open(self.yaml_fname, "w")
        ofh.write(yaml.dump(self.fixturize(index)))
        ofh.close()

    def fixturize(self, index, lang="fi"):
        """Convert the human readable course definitions to Django fixtures"""
        def clean_fname(fname):
            # FIXME: hardcoded path
            return re.sub(
                self.media_target_dir, "/static/generated_assets", fname)

        fy = []
        eidx = 0
        cidx = 0
        lidx = -1

        for doc in index:
            for lang, ldoc in doc["languages"].items():
                fields_dict = {
                    "title" : ldoc["Title"],
                    "version" : doc["Version"],
                    "language": lang
                    }
                if "Outside_information" in ldoc:
                    oi = ldoc["Outside_information"]
                    assert "name" in oi and "link" in oi
                    fields_dict["outside_info_name"] = oi["name"]
                    fields_dict["outside_info_link"] = oi["link"]

                if "Instructions" in ldoc:
                    fields_dict["instructions"] = ldoc["Instructions"]

                lidx += 1
                fy.append({"model": "exercise.Lecture",
                            "pk": lidx,
                            "fields": fields_dict
                           })

                for e in doc["Exercises"]:
                    e["correct"] = True
                    for c in e["confusers"]:
                        c["correct"] = False

                    alts = [e] + e["confusers"]
                    random.shuffle(alts)

                    #print repr(e)
                    fy.append({"model": "exercise.Exercise",
                              "pk": eidx,
                              "fields": {
                                "title" : e["name"][lang],
                                "question_type" : e["question_type"],
                                "lecture" : lidx,
                                "question_mp3" : clean_fname(e["mp3"]),
                                "question_ogg" : clean_fname(e["ogg"]),
                                "question_image": clean_fname(e["image_png"]),
                                "text": e["text"][lang] \
                                  if "text" in e and e["text"] else ""
                                }})

                    for a in alts:
                        fields = {
                          "answer_type" : e["answer_type"],
                          "exercise" : eidx,
                          "correct" : a["correct"]}

                        fields["image"] = clean_fname(a["image_png"])
                        fields["ogg"] = clean_fname(a["ogg"])
                        fields["mp3"] = clean_fname(a["mp3"])
                        fields["text"] = a["text"][lang] \
                          if "text" in a and a["text"] else ""
                        fy.append({"model" : "exercise.Choice",
                                  "pk" : cidx,
                                  "fields" : fields})
                        cidx += 1
                    eidx += 1
        return fy


class SimpleHtmlTarget(BuildTarget):
    """Create simple raw html pages for debugging."""
    html_template = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html lang="en-US" xml:lang="en-US" xmlns="http://www.w3.org/1999/xhtml">
    <head>
    </head>
    <body>
    %s
    </body>
  """

    def __init__(self, htmlfile="simple_html/index.html"):
        super(SimpleHtmlTarget, self).__init__(
          None, "simple_html/media/", "simple_html/media", "simple_html/media")
        self.htmlfile = htmlfile

        try:
          os.mkdir("simple_html")
          os.mkdir("simple_html/media")
        except OSError:
          pass

    def write(self, content_index):
        """Write the web pages and the corresponding media"""
        def clean_fname(fname):
            return re.sub('^simple_html/', '', fname)

        def image_str(fname):
            return '<img src="%s"></img>' % clean_fname(fname)

        def audio_str(oggname, mp3name):
            return """<audio controls="controls">
<source src="%s" type="audio/ogg" />
<source src="%s" type="audio/mpeg" />
<a href="%s">Play</a></audio>""" % (
    clean_fname(oggname), clean_fname(mp3name), clean_fname(mp3name))


        s = ""
        s += "<h2>Musical Notation Trainer</h2>\n"
        s += "<ul>\n"
        for d in content_index:
            s += "<li>%s (%d exercises)</li>\n" % (
                d["languages"]["en"]["Title"], len(d["Exercises"]))
        s += "</ul>\n"
        s += "</p>\n\n"

        for d in [doc for doc in content_index if len(doc["Exercises"]) > 0]:
            s += "<h2>%s</h2>\n" % d["languages"]["en"]["Title"]
            for e in d["Exercises"]:
                s += "<h3>%s</h3>\n" % e["name"]["en"].capitalize()
                s += '<table cellpadding="10" border="1">\n'
                s += '<tr><td colspan="3" align="center">'
                if e["question_type"] == "audio":
                    s += audio_str(e["ogg"], e["mp3"])
                else:
                    s += image_str(e["image_png"])
                s += "</td></tr>\n"
                alternatives = []
                for a in [e] + e["confusers"]:
                    text = a["text"]["en"] \
                      if "text" in a and a["text"] else None
                    if e["answer_type"] == "image":
                        alternatives.append(
                            (image_str(a["image_png"]),
                             audio_str(a["ogg"], a["mp3"]), text))
                    elif e["answer_type"] == "audio":
                        alternatives.append(
                            (audio_str(a["ogg"], a["mp3"]),
                             image_str(a["image_png"]), text))
                s += "<tr>\n"

                # FIXME: randomize order
                s += '<td align="center">' + '</td>\n<td align="center">'.join(
                    [atmp[0] for atmp in alternatives])+"</td>"
                s += "</tr>\n"
                if any([atmp[2] for atmp in alternatives]):
                    s += "<tr>\n"
                    s += '<td align="center">' + (
                          '</td>\n<td align="center">'.join(
                              [atmp[2] for atmp in alternatives])+"</td>")
                    s += "</tr>\n"


                s += "<tr>\n"
                s += '<td align="center">' + '</td>\n<td align="center">'.join(
                    [atmp[1] for atmp in alternatives])+"</td>"
                s += "</tr>\n"
                s += "</table></p>\n"

        fh = open(self.htmlfile, "w")
        fh.write(self.html_template %s)


class Content:
    """Parse the content definitions and create the associated files"""
    random_instruments = [
        "acoustic grand", "acoustic guitar (nylon)",
        "electric grand", "acoustic guitar (steel)", "harpsichord"] #, "xylophone"]

    transpose_major = ["d", "e", "f", "g,", "a,", "bis,"]

    naturalize_transpose_ly = """
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

    lilypond_template = """
\\version "2.12.3"
\\paper {
  indent = 0\\mm
  line-width = 60\\mm
  oddHeaderMarkup = ""
  evenHeaderMarkup = ""
  oddFooterMarkup = ##f
  evenFooterMarkup = ""
}
""" + naturalize_transpose_ly + """
\\score {
  \\new %s {
    \\set Staff.midiInstrument = "%s"
  { %s } }
 \\layout {}
 \\midi {}
}
"""

    def __init__(self, target=PureDjangoTarget(), lecture=None,
                 fname='content/course_directory.yaml',
                 host_type="macports", only_new=False):
        fh = open(fname, 'r')
        self.index = [i for i in yaml.load_all(fh)]
        fh.close()
        if lecture:
            self.index = [i for i in self.index
                            if i["languages"]["en"]["Title"] == lecture]

        for d in self.index:
            if not "Exercises" in d:
                d["Exercises"] = []

        self.content_dir = os.path.dirname(fname)
        if host_type == "macports":
            self.binpath = "/opt/local/bin"
            self.timidity_path = "/opt/local/bin"
        elif host_type == "linux":
            self.binpath = "/usr/bin"
            self.timidity_path = self.binpath
        self.target = target
        self.only_new = only_new

    def generate_extra_rounds(self):
        for d in self.index:
            if "Rounds" in d:
                if d["Rounds"][0] != "normal":
                    exercise_template = copy.deepcopy(d["Exercises"])
                    roundskip = 0
                else:
                    exercise_template = d["Exercises"]
                    roundskip = 1
            else:
                d["Rounds"] = ["normal"]
                roundskip = 1

            for r in d["Rounds"][roundskip:]:
                tmp_exercises = copy.deepcopy(exercise_template)
                if r == "transpose random":
                    transpose = "random"
                else:
                    transpose = False

                for e in tmp_exercises:
                    if transpose:
                        if transpose == "random":
                            tstring = \
                                "\\naturalizeMusic \\transpose c %s { " % (
                                    random.choice(self.transpose_major))
                        else:
                            assert False
                    e["notes"] = tstring + e["notes"] + " }"
                    for a in e["confusers"]:
                        a["notes"] = tstring + a["notes"] +" }"
                d["Exercises"].extend(tmp_exercises)

    def content2string(self):
        s = ""
        for d in self.index:
            exercises = d["Exercises"]
            s += "%s (%d exercises)\n" % (
                d["languages"]["en"]["Title"], len(exercises))
            for e in exercises:
                s += "  %s: question type '%s', answer type '%s'\n" % (
                    e["name"],
                    e["question_type"] if "question_type" in e else "random",
                    e["answer_type"] if "answer_type" in e else "random")
                s += "    Reference: '%s'\n" % e["notes"]
                s += "    Confusers: "
                s += ', '.join([repr(c["notes"]) for c in e["confusers"]]) +"\n"


        #    for ename, sublist in e.items():
        #      s += "  " +ename + ":" + repr(sublist) + "\n"
        return s

    @classmethod
    def augment_missing_info(cls, e):
        if not "question_type" in e or e["question_type"] == "random":
            # Give audio question a 66% prob
            e["question_type"], e["answer_type"] = random.choice(
                [("image", "audio"), ("audio", "image"), ("audio", "image")])
            e["generate_check"] = "random"

        if not "instrument" in e or e["instrument"] == "random":
            e["instrument"] = random.choice(Content.random_instruments)

        for c in e["confusers"]:
            if not "instrument" in c:
                c["instrument"] = e["instrument"]
            if not "tempo" in c and "tempo" in e:
                c["tempo"] = e["tempo"]
            if not "hidden_tempo" in c and "hidden_tempo" in e:
                c["hidden_tempo"] = e["hidden_tempo"]
            if "style" in e:
                c["style"] = e["style"]

    def expand_alternative_questions(self):
        def replace_media(orig, new):
            orig["notes"] = new["notes"]
            orig["image_png"] = new["image_png"]
            orig["ogg"] = new["ogg"]
            orig["mp3"] = new["mp3"]
            orig["text"] = new["text"] if "text" in new else None

        for d in self.index:
            tmp_exercises = d["Exercises"]
            d["Exercises"] = []
            for e in tmp_exercises:
                if not "generate" in e or e["generate"] == "single":
                    d["Exercises"].append(e)
                    continue

                all_alts = [e] + e["confusers"]
                m = re.match(r'(\d+) first', e["generate"])
                if m:
                    range_limit = int(m.group(1))
                else:
                    range_limit = len(all_alts)

                randomize_type = "generate_check" in e and \
                  e["generate_check"] == "random"
                permutations = [e]

                for i in range(1, range_limit):
                    e_tmp = copy.deepcopy(e)
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
                    for i2 in range(0, len(others)):
                        replace_media(e_tmp["confusers"][i2], others[i2])
                    permutations.append(e_tmp)

                random.shuffle(permutations)
                for i, p in enumerate(permutations):
                    #print repr(p)
                    for lang in p["name"].keys():
                        p["name"][lang] += " %d" % (i+1)
                    d["Exercises"].append(p)

    def compile(self):
        self.generate_extra_rounds()
        for d in self.index:
            to_png = []
            for e in d["Exercises"]:
                self.augment_missing_info(e)
                to_png.extend([e] + e["confusers"])

            lytmp = os.path.join(self.target.workdir, "tmp.ly")
            pngtmp = os.path.join(self.target.workdir, "tmp.png")
            miditmp = os.path.join(self.target.workdir, "tmp.midi")


            for i, conv in enumerate(to_png):
                #print repr(d["languages"]["en"]["Title"])
                title_us = re.sub(r"\s", "_", d["languages"]["en"]["Title"])
                conv["image_png"] = os.path.join(
                    self.target.pngdir, "%s-%d.png" % (title_us, i))
                conv["image_svg"] = os.path.join(
                    self.target.pngdir, "%s-%d.svg" % (title_us, i))
                conv["mp3"] = os.path.join(
                    self.target.mp3dir, "%s-%d.mp3" % (title_us, i))
                conv["ogg"] = os.path.join(
                    self.target.mp3dir, "%s-%d.ogg" % (title_us, i))

                if not (self.only_new and os.path.isfile(conv["image_png"])
                        and os.path.isfile(conv["mp3"]) and
                        os.path.isfile(conv["mp3"])):
                    lyfh = open(lytmp, "w")
                    body = ""
                    if "tempo" in conv:
                        body += "\\tempo 4 = %d" % conv["tempo"]
                    if "hidden_tempo" in conv:
                        body += "\\set Score.tempoHideNote = ##t "\
                          "\\tempo 4 = %d " % conv["hidden_tempo"]


                    if "style" in conv:
                        s = conv["style"]
                        if s == "chord":
                            body += r"\key c \major << { \\chordmode { " +\
                               conv["notes"] + " } } "
                            #body += "\\chordmode { " + conv["notes"] + " } >> "
                        if s == "interval" or s == "scale":
                            body += r" \key c \major << { " +\
                               conv["notes"] + " } "

                        if s == "chord" or s == "interval" or s == "scale":
                            body += r"\\addlyrics { " + conv["annotation"] +\
                              " } >>"

                        if s == "drums":
                            #body += "\\new DrumStaff { \drummode { " + conv["notes"] + "} }"
                            body += "{ \drummode { " + conv["notes"] + "} }"
                            staffstring = "DrumStaff"
                        else:
                            staffstring = "Staff"

                    else:
                        body += conv["notes"]
                        staffstring = "Staff"
                    lyfh.write(self.lilypond_template % (
                        staffstring, conv["instrument"], body))
                    lyfh.close()

                    fnull = open(os.devnull, 'w')

                    if True: # Generate png images
                        cmd = "%s/lilypond --png -dpixmap-format=pngalpha %s" %\
                          (self.binpath, os.path.basename(lytmp))
                        sys.stderr.write(cmd+"\n")
                        subprocess.call(cmd.split(), cwd=self.target.workdir,
                                        stdout=fnull, stderr=fnull)
                        cmd = "%s/convert %s -trim %s" % (
                            self.binpath, pngtmp, conv["image_png"])
                        subprocess.call(cmd.split(), stdout=fnull)

                    if False: # Generate svg images
                        cmd = "%s/lilypond -dbackend=svg %s" % (
                            self.binpath, os.path.basename(lytmp))
                        sys.stderr.write(cmd)
                        subprocess.call(cmd.split(), cwd=self.target.workdir,
                                        stdout=fnull, stderr=fnull)
                        st = SvgTransform.init_from_file("work/tmp.svg")
                        st.crop()
                        sys.stderr.write(conv["image_svg"]+"\n")
                        st.write(conv["image_svg"])

                    soxbase = "%s/sox -t raw -r 44100 -b 24 -e signed-integer "\
                      "-c 1 -" % self.binpath + " %s"
                    timidity_base = "%s/timidity %s -Or2slM -o - -s 44100 "\
                      "--volume-compensation" % (self.timidity_path, miditmp)

                    cmd = "%s| %s" % (timidity_base, soxbase % conv["mp3"])
                    sys.stderr.write(cmd+"\n")
                    subprocess.call(cmd, shell=True, stdout=fnull)

                    cmd = "%s | %s" % (timidity_base, soxbase% conv["ogg"])
                    subprocess.call(cmd, shell=True, stdout=fnull)
                    fnull.close()

        self.target.copy_files()
        self.expand_alternative_questions()
        self.target.write(self.index)

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "%prog [options]"
    version ="%prog v0.1"
    description = "Creates content for music training."

    target_choices = ["puredjango", "simple_html"]
    host_types = ["macports", "linux"]

    parser = OptionParser(usage=usage, version=version, description=description)
    parser.add_option("-t", "--target", help="Generate content for which format. Options: "+ repr(target_choices) +", default \"%default\".", choices=target_choices, default=target_choices[0])
    parser.add_option("-l", "--lecture", help="Generate content only for LECTURE", metavar="LECTURE", default=None)
    parser.add_option("-n", "--only_new", action="store_true", help="Generate files only for missing stuff.")
    parser.add_option(
      "-H", "--host_type", choices=host_types, default=host_types[0],
      help="Host type for setting the paths to binaries. Options: " +
    repr(host_types) + ", default =\"%default\".")


    (options, args) = parser.parse_args()
    if len(args)!=0:
        parser.error('Weird number of arguments, exit.')
        sys.exit(-1)

    if options.target == "puredjango":
        t = PureDjangoTarget()
    elif options.target == "simple_html":
        t = SimpleHtmlTarget()

    content = Content(t, lecture=options.lecture,
                      only_new=options.only_new, host_type=options.host_type)
    print(content.content2string())
    content.compile()

