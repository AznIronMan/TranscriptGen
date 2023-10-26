from argparse import Namespace


from core.audio import get_audio_path
from core.filer import (
    check_for_last_cache,
    file_check,
    generate_cache_file as get_cache_path,
    get_file_path as get_path,
    get_output_path,
    scratch_cleanup,
    write_to_file_with_ask as write_output,
)
from core.logger import log
from core.transcribe import (
    get_language as get_lang,
    get_transcription_type as get_tx_type,
    transcribe_audio,
    process_transcription as process_tx,
)
from core.utils import (
    cache_loader,
    cache_saver,
    file_timestamp,
    get_extension,
    gui_mode,
    notification,
    verbose_mode,
)
from core.zerr import zerr


def main(args: Namespace):
    # TODO: Fix FFMPEG in __main__.py
    # TODO: Add support converting languages (from audio source to other)
    # TODO: Add full GUI support
    try:
        gui = gui_mode()
        verbose = verbose_mode(args.verbose)

        file_path = get_path(
            args.file,
            "extractable",
            gui,
            verbose,
        )
        timestamp = file_timestamp()

        audio_path = get_audio_path(file_path, timestamp)

        confirm_audio_path = file_check(audio_path)
        if not confirm_audio_path[0]:
            raise Exception(confirm_audio_path[1])

        last_cache = check_for_last_cache(gui)
        cache_file = (
            get_cache_path(timestamp) if last_cache is None else last_cache
        )

        if last_cache == cache_file:
            result = cache_loader(cache_file)
        else:
            result = transcribe_audio(audio_path, args.model, args.language)
            cache_saver(cache_file, result)

        if result is None:
            raise Exception(
                "Something went wrong while transcribing the audio "
                "as the transcription output is None."
            )

        transcription_type = get_tx_type(args.type, gui)
        language = get_lang(args.language)

        output_file_path = get_output_path(
            file_path, transcription_type, args.outputfolder
        )

        ext = get_extension(transcription_type)

        processed_content = process_tx(result, transcription_type, language)

        write_result = write_output(
            processed_content, output_file_path, ext, gui, verbose
        )

        if not write_result[0]:
            raise Exception(write_result[1])

        if file_check(output_file_path)[0]:
            scratch_cleanup()
            log(
                f"Transcription complete! Output file: [{output_file_path}]",
                success=True,
            )
            notification(
                msg="Transcription complete!", gui=gui, verbose=verbose
            )
        else:
            notification(
                "error", "Transcription failed!", gui=gui, verbose=verbose
            )
            raise Exception(
                f"Transcription failed! Output file: [{output_file_path}]"
            )

        return None
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return None
