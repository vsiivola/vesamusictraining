#!/usr/bin/env python
"""Creates the excercise contents."""

import multiprocessing
import logging
import os
import random
import subprocess

from svgtransform import SvgTransform

LOGGER = logging.getLogger(__name__)

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

LILYPOND_TEMPLATE = r"""
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

class LilySourceException(Exception):
    """Exception in handling Lilypond source file"""
    pass

def get_random_transpose_key():
    """Get a random key to transpose to."""
    return random.choice(TRANSPOSE_MAJOR)


class LilySource:
    """Generate the lilypond source and media files."""
    def __init__(self, notes, annotation, tempo=None, hidden_tempo=None, style=None,
                 instrument=None, transpose=None):
        self.notes = notes
        self.annotation = annotation
        self.tempo = tempo
        self.hidden_tempo = hidden_tempo
        self.style = style
        if not instrument or instrument == "random":
            self.instrument = random.choice(RANDOM_INSTRUMENTS)
        else:
            self.instrument = instrument
        self.transpose = transpose

    def eq_image(self, other):
        """Will the generated image be same."""
        return self.image_signature() == other.image_signature()

    def eq_sound(self, other):
        """Will the generated image be same."""
        return self.sound_signature() == other.sound_signature()

    def sound_signature(self):
        """We need something hashable for removing duplicate sounds"""
        return (self.notes, self.annotation, self.tempo, self.hidden_tempo,
                self.style, self.instrument, self.transpose)

    def image_signature(self):
        """We need something hashable for removing duplicate images"""
        return (self.notes, self.annotation, self.style, self.transpose)

    def str(self):
        """Create the source lilypond notation"""
        notes = self.notes
        if self.transpose:
            notes = r"\naturalizeMusic \transpose c %s { %s } " % (
                self.transpose, notes)

        body = ""
        if self.tempo:
            body += r"\tempo 4 = %d" % self.tempo

        if self.hidden_tempo:
            body += r"\set Score.tempoHideNote = ##t "\
              r"\tempo 4 = %d " % self.hidden_tempo

        if self.style:
            if self.style == "chord":
                body += r"\key c \major << { \chordmode { " + notes + " } } "
            elif self.style == "interval" or self.style == "scale":
                body += r" \key c \major << { " + notes + " } "

            if self.style == "chord" or self.style == "interval" or self.style == "scale":
                if self.annotation:
                    body += r"\addlyrics { " + self.annotation + " }"
                body += " >>"

            if self.style == "drums":
                body += r"{ \drummode { " + self.notes + "} }" # Drum notes should not be transposed
                staffstring = "DrumStaff"
            else:
                staffstring = "Staff"

        else:
            body += notes
            staffstring = "Staff"

        return LILYPOND_TEMPLATE % (staffstring, self.instrument, body)

class LilyCompileTask:
    """Single compilation task."""
    def __init__(self, lilysource, output_formats, tmp_fname, output_basename):
        self.lilysource = lilysource
        self.output_formats = output_formats
        self.tmp_fname = tmp_fname

        recognized_formats = 0
        if "png" in output_formats:
            self.png_fname = output_basename + ".png"
            recognized_formats += 1
        else:
            self.png_fname = None

        if "svg" in output_formats:
            self.svg_fname = output_basename + ".png"
            recognized_formats += 1
        else:
            self.svg_fname = None

        if "mp3" in output_formats:
            self.mp3_fname = output_basename + ".mp3"
            recognized_formats += 1
        else:
            self.mp3_fname = None

        if "ogg" in output_formats:
            self.ogg_fname = output_basename + ".ogg"
            recognized_formats += 1
        else:
            self.ogg_fname = None

        if len(output_formats) != recognized_formats or len(output_formats) == 0:
            raise LilySourceException("Request has unknown formats '%s'" % output_formats)

    def __str__(self):
        ostr = "LCT - source: %s" % self.lilysource
        if self.png_fname:
            ostr += ", png: " + self.png_fname
        if self.svg_fname:
            ostr += ", svg: " + self.svg_fname
        if self.mp3_fname:
            ostr += ", mp3: " + self.mp3_fname
        if self.ogg_fname:
            ostr = ", ogg: " + self.ogg_fname
        return ostr

def poolwrap_compile_one(argtuple):
    """A wrapper for media creation since multiprocessing.Pool
    cannot handle in-class functions."""
    cinstance, lytask = argtuple
    cinstance.compile_one(lytask)
    return True


class LilyCompiler:
    """Compile the media assets"""
    def __init__(self, lilypond_path, imagemagick_path, inkscape_path, timidity_path):
        self.lilypond_path = lilypond_path
        self.imagemagick_path = imagemagick_path
        self.inkscape_path = inkscape_path
        self.timidity_path = timidity_path

        self.sox_base = ["%s/sox" % self.imagemagick_path, "-t", "raw", "-r", "44100",
                         "-b", "24", "-e", "signed-integer", "-c", "1", "-"]

        self.timidity_base = ["%s/timidity" % self.timidity_path, None,
                              "-Or2slM", "-o", "-", "-s", "44100 ",
                              "--volume-compensation"]

    def compile(self, ly_tasklist, max_processes=1):
        """Compile a list of tasks."""
        if max_processes > 1:
            pool = multiprocessing.Pool(processes=max_processes)
            pool.map(poolwrap_compile_one, [(self, lytask) for lytask in ly_tasklist])
        else:
            for ly_task in ly_tasklist:
                self.compile_one(ly_task)

    def compile_one(self, ly_task):
        """Create the image and corresponding midi file from lilypond source."""
        with open(os.devnull, 'w') as fnull:
            LOGGER.debug(ly_task)
            if ly_task.png_fname:
                cmd = "%s/lilypond --png -dpixmap-format=pngalpha %s" % (
                    self.lilypond_path, os.path.basename(ly_task.lilysource))
                LOGGER.debug(cmd)
                if subprocess.call(cmd.split(), cwd=os.path.dirname(ly_task.tmp_fname),
                                   stdout=fnull, stderr=fnull):
                    raise LilySourceException("Failed '%s'" % cmd)
                LOGGER.debug(cmd)
                cmd = "%s/convert %s -trim %s" % (
                    self.imagemagick_path, ly_task.tmp_fname+".png", ly_task.png_fname)
                if subprocess.call(cmd.split(), stdout=fnull, stderr=fnull):
                    raise LilySourceException("Failed '%s'" % cmd)

            if ly_task.svg_fname:
                cmd = "%s/lilypond -dbackend=svg %s" % (
                    self.lilypond_path, os.path.basename(ly_task.lilysource))
                LOGGER.debug(cmd)
                if subprocess.call(cmd.split(), cwd=os.path.dirname(ly_task.tmp_fname),
                                   stdout=fnull, stderr=fnull):
                    raise LilySourceException("Failed '%s'" % cmd)
                strans = SvgTransform.init_from_file(ly_task.tmp_fname+".svg", self.inkscape_path)
                strans.crop()
                strans.write(ly_task.svg_fname)

            if not ly_task.png_fname and not ly_task.svg_fname:
                # Need to run lilypond with some params to get the midi file
                # even if no image is requested
                cmd = "%s/lilypond --png -dpixmap-format=pngalpha %s" % (
                    self.lilypond_path, os.path.basename(ly_task.lilysource))
                LOGGER.debug(cmd)
                if subprocess.call(cmd.split(), cwd=os.path.dirname(ly_task.tmp_fname),
                                   stdout=fnull, stderr=fnull):
                    raise LilySourceException("Failed '%s'" % cmd)


            # Set the source lilypond filename to the correct slot in the template
            timidity_cmd = self.timidity_base[:1] + [ly_task.tmp_fname + ".midi"] \
                           + self.timidity_base[2:]

            for afname in [ly_task.mp3_fname, ly_task.ogg_fname]:
                if not afname:
                    continue
                LOGGER.debug("timidity open %s", timidity_cmd)
                timidityp = subprocess.Popen(timidity_cmd, stdout=subprocess.PIPE, stderr=fnull)
                LOGGER.debug("sox open %s", self.sox_base)
                soxp = subprocess.Popen(self.sox_base + [afname],
                                        stdin=timidityp.stdout)
                soxp.communicate()
                timidityp.communicate()
                if timidityp.returncode:
                    raise RuntimeError("Failed timidity '%s'" %
                                       " ".join(self.timidity_base))
                if soxp.returncode:
                    raise RuntimeError("Failed sox '%s'" %
                                       " ".join(self.sox_base + [afname]))

