VesaMusicTutor is a simple multiple choice html5 web app, 
that is designed to teach or refresh the basic concepts
of rhythm, notes and harmony and their musical notation.

The code is currently in somewhat rought shape.

You'll need python2, python-yaml, lilypond, timidity and 
sox to generate the exercises.

Running "create_book.py" will generate a django web 
application that can be controlled as per usual 
django practices. The option -H can be used to specify
the host type, which affects the paths where the
binaries for lilypond, timidity and sox are assumed to
exist. The option "-t simple_html" will generate a 
rough web page for debugging.

