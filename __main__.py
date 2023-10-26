import os
import sys
from pathlib import Path

# Changable Variables

force_debug_mode = False  # change to True to force debug mode
ffmpeg_dir = (
    "./assets/ffmpeg"  # change to absolute or relative path to ffmpeg binary
)
log_folder_name = ".logs"  # change to desired log folder name
scratch_dir = "./scratch"  # change to desired scratch folder name


# Changable But Not Recommended To Change Variables
# (unless you know what you're doing)


audio_file_types_ffmpeg = (
    ".3g2,.3gp,.aac,.ac3,.flac,.m4a,.m4b,.m4r,.mka,.mp3,.mp4,.ogg,"
    ".ga,.opus,.ra,.ram,.wav,.wma"
)
audio_file_types_whisper = ".flac,.m4a,.mp3,.ogg,.wav"

ffmpeg_linux_binary_download_url = (
    "https://johnvansickle.com/ffmpeg/releases/"
    "ffmpeg-release-amd64-static.tar.xz"
)  # .tar.xz
ffmpeg_mac_binary_download_url = "https://evermeet.cx/ffmpeg/get"  # .7z
ffmpeg_win_binary_download_url = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/"
    "latest/ffmpeg-master-latest-win64-gpl.zip"
)  # .zip

video_file_types_ffmpeg = (
    ".3g2,.3gp,.asf,.avi,.dv,.f4v,.flv,.m2ts,.m4v,.mkv,.mov,.mp4,"
    ".mpeg,.mpg,.mts,.mxf,.ogv,.rm,.rmvb,.ts,.vob,.webm,.wmv"
)
video_file_types_moviepy = ".avi,.mkv,.mov,.mp4,.ogv"

# *** DO NOT EDIT BELOW THIS LINE ***

os.environ["FFMPEG_AUDIO_TYPES"] = audio_file_types_ffmpeg
os.environ["FFMPEG_DIR"] = ffmpeg_dir if ffmpeg_dir else "./ffmpeg"
os.environ["FFMPEG_LINUX"] = ffmpeg_linux_binary_download_url
os.environ["FFMPEG_MAC"] = ffmpeg_mac_binary_download_url
os.environ["FFMPEG_VIDEO_TYPES"] = video_file_types_ffmpeg
os.environ["FFMPEG_WIN"] = ffmpeg_win_binary_download_url
os.environ["FORCE_DEBUG"] = "False" if not force_debug_mode else "True"
os.environ["LOG_DIR"] = log_folder_name if log_folder_name else ".logs"
os.environ["LOCAL_TEMP"] = scratch_dir if scratch_dir else "./scratch"
os.environ["MOVIEPY_VIDEO_TYPES"] = video_file_types_moviepy
os.environ["WHISPER_AUDIO_TYPES"] = audio_file_types_whisper

current_path = Path(__file__).resolve()
parent_path = current_path.parent

sys.path.append(str(parent_path))

if __name__ == "__main__":
    import argparse
    from core.app import main as process

    # TODO: Fix the FFMPEG download
    # from core.filer import dir_check
    # from core.utils import download_latest_ffmpeg

    # ffmpeg_dir = os.environ.get("FFMPEG_DIR", "./ffmpeg")
    # if not dir_check(ffmpeg_dir)[0]:
    #     result = download_latest_ffmpeg()
    #     if not result:
    #         print("Error downloading ffmpeg")
    #         sys.exit(1)

    os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_dir)

    parser = argparse.ArgumentParser(
        description="Transcription of " "video/audio files"
    )
    parser.add_argument("-f", "--file", help="Path to the video/audio file")
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="en",
        help="Language code of the audio file (default: en)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="base",
        help="Whisper Model name (default: base)",
    )
    parser.add_argument(
        "-o",
        "--outputfolder",
        type=str,
        help="Output folder for the transcription file "
        "(default: same folder as the input file)",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="The output format (0: transcript only, "
        "1: transcript with time, 2: .srt file)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        choices=[0, 1],
        default=0,
        help="Verbose output (0: off, 1: on)",
    )
    args = parser.parse_args()

    process(args)
