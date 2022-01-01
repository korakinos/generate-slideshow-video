from datetime import date, datetime, time, timedelta
import ffmpeg
import fnmatch
from os import listdir, path, rename
from time import strftime
from unicodedata import normalize


# configuration
# (A few options are configurable via the following variables, some are still hard-coded.)
slide_period = timedelta(seconds=5)
photo_dir = "./Photos/"
photo_file_extension = ".jpg"
srt_file = "subtitles.srt"
font = "Liberation Sans"
outline = "0.2"
resolution = "hd1080"  # see https://ffmpeg.org/ffmpeg-utils.html#video-size-syntax for valid values
video_file = "slideshow-outline-" + outline + "-resolution-" + resolution + ".mp4"


# list photos in alphabetical order (hopefully matching ffmpeg's glob below!)
photo_list = sorted(fnmatch.filter(listdir(photo_dir), "*" + photo_file_extension))


# backup previously generated files
try:
    rename(srt_file, "backup-" + strftime("%FT%T") + "-" + srt_file)
    rename(video_file, "backup-" + strftime("%FT%T") + "-" + video_file)
except FileNotFoundError:
    pass


# generate SRT subtitles from filenames
with open(srt_file, "a") as srt:
    for index in range(len(photo_list)):
        position = datetime.combine(
            date.today(), time(0, 0, 0)
        )  # https://stackoverflow.com/posts/656394/revisions
        position += index * slide_period
        timestring = (
            position.strftime("%H:%M:%S,000")
            + " --> "
            + (position + slide_period).strftime("%H:%M:%S,000")
        )

        # write to SRT file, Unicode-normalizing the filename (as ffmpeg doesn't 
        # handle composite umlauts in subtitles gracefully)
        srt.write(
            str(index + 1)
            + "\n"
            + timestring  # SRT numbering starts at 1, not 0.
            + "\n"
            + normalize("NFC", path.splitext(photo_list[index])[0])
            + "\n"
            + "\n"
        )
#    # The following would create a text file as input for the ffmpeg concat demuxer,
#    # which this is script isn't using. The main advantage would be to have full
#    # control that the order of images and subtitles match (right now this script
#    # relies on the output of python's "sorted" to agree with the ordering of
#    # ffmpeg's "pattern_type=glob"). If you want to us it, add the with statement
#    # "with open("ffmpeg-concat.txt", "a") as concat_file:" above.
#
#        concat_file.write("file '" + photo_list[index] + "'\n" +
#                          "duration " + str(slide_period) + "\n")
#
#    # The last filename has to be repeated due to ffmpeg quirk (see https://trac.ffmpeg.org/wiki/Slideshow#Concatdemuxer ).
#    concat_file.write("file '" + photo_list[-1] + "'")


# generate slideshow video
(
    ffmpeg.input(
        photo_dir + "*" + photo_file_extension, pattern_type="glob", framerate=1 / 5
    )
    .filter("scale", size=resolution)
    #.filter("pad", 1920, 1080, -1, -1, color="black")
    .filter("format", "yuv420p")
    .filter("fps", fps=25)
    .filter(
        "subtitles",
        srt_file,
        fontsdir="/usr/share/fonts",
        force_style="Alignment=1, fontname=" + font + ",Outline=" + outline,
    )
    .output(video_file)
    .run()
)
