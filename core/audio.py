import os


from pydub import AudioSegment


from core.filer import file_check
from core.logger import log
from core.utils import (
    get_file_type_dict as file_types_dict,
    scratch_path as get_temp_dir,
)
from core.video import extract_audio_from_video as extract_audio, prep_video
from core.zerr import zerr


def get_audio_path(filepath: str, timestamp: str) -> str:
    types_dict = file_types_dict()
    if filepath.endswith(tuple(types_dict["ffmpeg_v"])):
        verified_video_file = prep_video(filepath, timestamp)
        audio_path = extract_audio(verified_video_file, timestamp)
    elif filepath.endswith(tuple(types_dict["ffmpeg_a"])):
        audio_path = prep_audio(filepath, timestamp)
    elif filepath is None or filepath == "":
        raise Exception("No file selected.")
    else:
        raise Exception(f"[{filepath}] is an unsupported file type.")
    if audio_path is None or audio_path == "":
        raise Exception("No audio file selected.")
    return audio_path


def prep_audio(filepath: str, timestamp: str):
    types_dict = file_types_dict()
    temp_dir = get_temp_dir()
    try:
        if not filepath.endswith(tuple(types_dict["whisper"])):
            raise Exception(
                f"[{filepath}] is not a supported audio file type."
            )
        else:
            audio = AudioSegment.from_file(filepath)
            converted_audio_path = os.path.join(
                temp_dir, f"{timestamp}_audio_converted.wav"
            )
            audio.export(converted_audio_path, format="wav")
            audio.close()
            file_check_result = file_check(converted_audio_path)
            if not file_check_result[0]:
                raise Exception(file_check_result[1])
            else:
                log(
                    f"Audio [{filepath}] successfully converted "
                    f"to Audio [{converted_audio_path}] for audio prep",
                    success=True,
                )
                return converted_audio_path
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)
