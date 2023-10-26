import srt
import whisper_timestamped as whisper


from datetime import timedelta

from core.logger import log
from core.utils import (
    console_question as ask_q,
    yesno_popup_ask as ask_yn,
)
from core.zerr import zerr


def get_language(lang: str) -> str:
    # TODO: Add support for more languages
    try:
        if lang is None or lang == "":
            lang = "en"
        return lang
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return "en"


def get_transcription_type(type: int, gui: bool = False) -> int:
    try:
        if type > 2 or type < 0 or type is None:
            if gui:
                output_format = ask_yn(
                    "Do you want the transcription in .srt format?"
                )

            else:
                output_format = ask_q(
                    "Do you want the transcription in .srt format? (y/n): ",
                    "yesno",
                )
            if output_format:
                second_output_format = False
                type = 2
            else:
                if gui:
                    second_output_format = ask_yn(
                        "Do you want the transcription with timestamps?"
                    )
                else:
                    second_output_format = ask_q(
                        "Do you want the transcription with timestamps? "
                        "(y/n): ",
                        "yesno",
                    )

                if second_output_format:
                    type = 1
                else:
                    type = 0

            if output_format:
                type = 2
            elif second_output_format:
                type = 1
            else:
                type = 0

        return type
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return 1


def process_transcription(transcribedresults, type: int, lang: str):
    try:
        if (
            type == 0 or type == 1 or type == 2
        ):  # 0 (text), 1 (text + time), 2 (.srt)
            segments = []
            for i, seg in enumerate(transcribedresults["segments"]):
                start_time = timedelta(seconds=seg["start"])
                end_time = timedelta(seconds=seg["end"])
                content = seg["text"]
                if lang != "en":
                    # TODO: add support for translating to other languages
                    pass  # remove when TODO is implemented
                if type == 2:
                    segments.append(
                        srt.Subtitle(i, start_time, end_time, content)
                    )
                elif type == 1:
                    segments.append(f"{start_time} - {end_time}: {content}")
                elif type == 0:
                    segments.append(content)
                else:
                    raise Exception(f"Unsupported output format: type[{type}]")
            if type == 2:
                return srt.compose(segments)
            elif type == 0 or type == 1:
                return "\n".join(segments)
            else:
                raise Exception(f"Unsupported output format: type[{type}]")
        else:
            raise Exception(f"Unsupported output format: type[{type}]")
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def transcribe_audio(audiopath: str, modelname: str, lang: str):
    try:
        audio = whisper.load_audio(audiopath)
        model = whisper.load_model(modelname)
        return whisper.transcribe(model, audio, language=lang)
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)
