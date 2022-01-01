An unpolished python script I used to generate a slideshow video from image files with subtitles generated from their filenames. All configuration (file path, font, resolution, fps...) has to be done directly in the code, there are no command-line arguments.

Unicode normalisation is done on the subtitles to avoid misalignment of umlaut diacritics by ffmpeg.

## Dependencies (python modules)

 - ffmpeg
