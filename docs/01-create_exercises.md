# Generating the exercises

The lectures are generated from the yaml files in the content directory.

## Install dependencies

The yaml files are parsed in python - thus you need **python 3** and **pyyaml**.

The lecture yaml files contain the written music in **lilypond** notation. If you want to generate images in vector format (svg), you need a quite recent version of lilypond that has fixed the bugs that earlier svg backends had. At least version 2.18.2. is known to work. If you use png images, **Imagemagick** is used to crop the images.

Lilypond can also generate midi files. These midi files are converted to mp3 and ogg using **timidity** and **sox**. The default midi sound banks coming with timidity are not of the highest possible quality, but they have been used to generate the sounds at the live app page. You may want to configure timidity to access other midi sound banks if you have access to them.

## Generate the exercises

Run scripts/create_book.py to generate the exercises. The -h flag will show the available options. You can generate the content for the full blown web app, or just generate a single html page for debuggin purposes.
