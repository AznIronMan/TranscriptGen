import os
import moviepy.editor as mp


from core.filer import file_check
from core.logger import log
from core.utils import (
    get_file_type_dict as file_types_dict,
    scratch_path as get_temp_dir,
)
from core.zerr import zerr


def extract_audio_from_video(filepath: str, timestamp: str):
    types_dict = file_types_dict()
    temp_dir = get_temp_dir()
    try:
        if not filepath.endswith(tuple(types_dict["moviepy"])):
            raise Exception(
                f"[{filepath}] is not a supported video file type."
            )
        else:
            clip = mp.VideoFileClip(filepath)
            audio_path = os.path.join(temp_dir, f"{timestamp}_audio.wav")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if clip.audio is not None:
                clip.audio.write_audiofile(audio_path)
                clip.close()
                file_check_result = file_check(audio_path)
                if not file_check_result[0]:
                    raise Exception(file_check_result[1])
                else:
                    log(
                        f"Audio [{audio_path}] successfully extracted from "
                        f"[{filepath}]",
                        success=True,
                    )
                    return audio_path
            else:
                raise Exception("The video file does not contain audio")
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def prep_video(filepath: str, timestamp: str):
    types_dict = file_types_dict()
    temp_dir = get_temp_dir()
    try:
        if not filepath.endswith(tuple(types_dict["moviepy"])):
            clip = mp.VideoFileClip(filepath)
            converted_file_path = os.path.join(
                temp_dir, f"{timestamp}_converted.mp4"
            )
            clip.write_videofile(converted_file_path)
            clip.close()
            file_check_result = file_check(converted_file_path)
            if not file_check_result[0]:
                raise Exception(file_check_result[1])
            else:
                log(
                    f"Video [{filepath}] successfully converted to "
                    f"Video [{converted_file_path}] for video prep",
                    success=True,
                )
                return converted_file_path
        elif filepath.endswith(tuple(types_dict["moviepy"])):
            file_check_result = file_check(filepath)
            if not file_check_result[0]:
                raise Exception(file_check_result[1])
            else:
                return filepath
        else:
            raise Exception(
                f"[{filepath}] is not a supported video file type."
            )
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)
