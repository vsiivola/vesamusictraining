#!/usr/bin/env python
"""Creates the excercise contents."""

import logging

from content import Content
#from media_resources import MediaResourceHandler
from lilypond_source import LilyCompiler

from resource_simplehtml import SimpleHtmlTarget
from resource_django import PureDjangoTarget
from resource_android import AndroidResourceTarget


LOGGER = logging.getLogger(__name__)

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
                        help="Generate content only for LECTURE "\
                        "(or list of semicolon separated lectures)",
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

    # Parse and expand the YAML files
    content = Content(lectures=set(args.lecture.split(";")) if args.lecture else None)
    content.expand()

    if args.target == "puredjango":
        target = PureDjangoTarget()
    elif args.target == "simple_html":
        target = SimpleHtmlTarget()
    elif args.target == "android":
        target = AndroidResourceTarget()

    target.include_images(content.fixed_images)
    sound_tasks, image_tasks = target.media_compile_tasklist(
        [e["lysrc"] for e in content.get_questions_and_choices()])
    content.insert_filenames(sound_tasks, image_tasks)
    target.write(content.index)

    if args.host_type == "macports":
        binpath = "/opt/local/bin"
    elif args.host_type == "linux":
        binpath = "/usr/bin"

    timidity_path = binpath
    lilypond_path = binpath
    inkscape_path = binpath
    imagemagick_path = binpath
    if args.lilypond_path:
        lilypond_path = args.lilypond_path

    lcc = LilyCompiler(lilypond_path, imagemagick_path, inkscape_path, timidity_path)
    lcc.compile(list(sound_tasks.values()) + list(image_tasks.values()))









