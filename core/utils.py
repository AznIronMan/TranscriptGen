import os
import pickle
import platform
import requests
import shutil
import tempfile


from datetime import datetime
from os import path
from tkinter import filedialog, messagebox, Tk
from typing import Iterable, Optional, Union


from core.logger import log
from core.zerr import zerr


def cache_loader(filepath: str) -> None:
    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def cache_saver(filepath: str, data: object) -> None:
    try:
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def console_question(
    question: str, type: Optional[str] = None
) -> Union[str, bool]:
    try:
        if type == "yesno":
            return input(f"{question} (y/n): ").lower().startswith("y")
        else:
            return str(input(f"{question}: "))
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def download_latest_ffmpeg(operating_system: Optional[str] = None) -> bool:
    try:
        os_name = get_os() if operating_system is None else operating_system

        download_url = ""
        if os_name == "Linux":
            download_url = os.environ.get("FFMPEG_LINUX")
        elif os_name == "Darwin":
            download_url = os.environ.get("FFMPEG_MAC")
        elif os_name == "Windows":
            download_url = os.environ.get("FFMPEG_WIN")
        else:
            raise Exception("Unsupported operating system")

        if download_url is None or download_url == "":
            raise Exception("No download URL found")

        ffmpeg_dir = os.environ.get("FFMPEG_DIR", "./ffmpeg")

        if not os.path.exists(ffmpeg_dir):
            os.makedirs(ffmpeg_dir)

        response = requests.get(download_url, timeout=10)
        response.raise_for_status()

        file_extension = os.path.splitext(download_url)[-1]
        if not file_extension:
            raise Exception(f"No file extension found in URL: {download_url}")

        target_filename = f"ffmpeg{file_extension}"

        if ffmpeg_dir:
            target_path = os.path.join(ffmpeg_dir, target_filename)
        else:
            ffmpeg_default_dir = get_internal_directory_path("ffmpeg", True)
            target_path = os.path.join(ffmpeg_default_dir, target_filename)

        with open(target_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        os.chmod(target_path, 0o755)

        log(f"{os_name} binary downloaded to {target_path}", success=True)

        return True
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def file_dialog_ask(
    types: Iterable[tuple[str, str | list[str] | tuple[str, ...]]] = [
        ("All files", "*.*")
    ],
    type: str = "open",
    initdir: Optional[str] = None,
) -> str:
    try:
        if type == "open":
            if initdir is not None:
                return filedialog.askopenfilename(
                    filetypes=types, initialdir=initdir
                )
            else:
                return filedialog.askopenfilename(filetypes=types)
        elif type == "save":
            if initdir is not None:
                return filedialog.asksaveasfilename(
                    filetypes=types, initialdir=initdir
                )
            else:
                return filedialog.asksaveasfilename(filetypes=types)
        else:
            raise Exception(f"Unsupported file dialog type: {type}")
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def file_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def get_extension(type: int = 0, options: list[str] = [".srt", ".txt"]) -> str:
    try:
        if type == 0 or type == 1:
            return options[1]
        elif type == 2:
            return options[0]
        else:
            raise Exception(f"Unsupported extension type: {type}")
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_file_type_dict() -> dict[str, list[str]]:
    return {
        "ffmpeg_a": get_file_types("ffmpeg", "audio"),
        "ffmpeg_v": get_file_types("ffmpeg", "video"),
        "moviepy": get_file_types("moviepy", "video"),
        "whisper": get_file_types("whisper", "audio"),
    }


def get_file_types(app: str, type: str) -> list[str]:
    try:
        if app == "ffmpeg":
            if type == "audio":
                return (
                    str(
                        os.environ.get(
                            "FFMPEG_AUDIO_TYPES", "*.mp3,*.ogg,*.wav"
                        )
                    )
                ).split(",")
            elif type == "video":
                return (
                    str(
                        os.environ.get(
                            "FFMPEG_VIDEO_TYPES", "*.mp4,*.mkv,*.avi"
                        )
                    )
                ).split(",")
            elif type is None or type == "":
                raise Exception(f"No file type specified for {app}")
            else:
                raise Exception(f"Unsupported file type for {app}: {type}")
        elif app == "whisper":
            if type == "audio":
                return (
                    str(
                        os.environ.get(
                            "WHISPER_AUDIO_TYPES", "*.mp3,*.ogg,*.wav"
                        )
                    )
                ).split(",")
            elif type is None or type == "":
                raise Exception(f"No file type specified for {app}")
            else:
                raise Exception(f"Unsupported file type for {app}: {type}")
        elif app == "moviepy":
            if type == "video":
                return (
                    str(
                        os.environ.get(
                            "MOVIEPY_VIDEO_TYPES", "*.mp4,*.mkv,*.avi"
                        )
                    )
                ).split(",")
            elif type is None or type == "":
                raise Exception(f"No file type specified for {app}")
            else:
                raise Exception(f"Unsupported file type for {app}: {type}")
        elif app is None or app == "":
            raise Exception("No app specified")
        else:
            raise Exception(f"Unsupported app: {app}")
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_internal_directory_path(
    destination: Optional[str], create: bool
) -> str:
    try:
        directory_path = destination if destination else os.getcwd()
        if destination is not None:
            if not path.isabs(destination):
                directory_path = path.join(os.getcwd(), destination)
        if not path.exists(directory_path):
            if create:
                os.makedirs(directory_path)
            else:
                raise Exception(f"Directory does not exist: {directory_path}")
        if not path.isdir(directory_path):
            raise Exception(
                (f"Destination is not a directory: {directory_path}")
            )
        return directory_path
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_os() -> str:
    return platform.system()


def get_sys_temp_dir() -> str:
    try:
        sys_temp_dir = tempfile.gettempdir()
        if (
            os.path.exists(sys_temp_dir)
            and os.path.isdir(sys_temp_dir)
            and os.access(sys_temp_dir, os.W_OK)
        ):
            return sys_temp_dir
        else:
            raise Exception(
                f"System temp directory [{sys_temp_dir}] is not writable"
            )
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def gui_mode() -> bool:
    if get_os() == "Linux" and os.environ.get("DISPLAY", "") == "":
        return False
    else:
        root = Tk()
        root.withdraw()
        return True


def msgbox(type: str = "info", msg: Optional[str] = None) -> None:
    try:
        if type.lower() == "info":
            messagebox.showinfo("TranscriptGen", msg if msg else "Success")
        elif type.lower() == "warning":
            messagebox.showwarning("TranscriptGen", msg if msg else "Warning")
        elif type.lower() == "error":
            messagebox.showerror("TranscriptGen", msg if msg else "Error")
        else:
            raise Exception(f"Unsupported message box type: {type}")
        return
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def notification(
    type: str = "info",
    msg: Optional[str] = None,
    gui: bool = False,
    verbose: bool = False,
) -> None:
    if gui and verbose:
        msgbox(type, msg)
    else:
        print(f"{type.upper()}: {msg}" if msg else f"{type.upper()}")
    return


def scratch_path() -> str:
    try:
        scratch_dir = os.environ.get("LOCAL_TEMP", "./scratch")
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
        if not os.path.isdir(scratch_dir):
            raise Exception(f"{scratch_dir} exists but is not a directory")
        if not os.access(scratch_dir, os.W_OK):
            raise Exception(f"{scratch_dir} is not writable")
        return scratch_dir
    except Exception as e:
        error_info = zerr(e) + "\nTrying system temp directory..."
        log(error_info, "ERROR")
        try:
            sys_temp_dir = get_sys_temp_dir()
            log(
                f"Using system temp directory [{sys_temp_dir}] "
                "as scratch directory",
                success=True,
            )
            return sys_temp_dir
        except Exception as e:
            error_info = zerr(e)
            log(error_info, "ERROR")
            raise Exception(error_info)


def verbose_mode(verbargument: Optional[int]) -> bool:
    try:
        if verbargument is None or verbargument == "":
            return False
        elif verbargument == 0:
            return False
        elif verbargument == 1:
            return True
        else:
            return False
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "INFO")
        return False


def yesno_popup_ask(question: str) -> bool:
    try:
        response = messagebox.askyesno("TranscriptGen", question)
        if response is None or response == "":
            return False
        return response
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return False
