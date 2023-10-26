import glob
import os
import shutil


from os import path
from typing import Optional, Tuple


from core.logger import log
from core.utils import (
    console_question as ask_q,
    file_dialog_ask as ask_box,
    get_file_type_dict as file_types_dict,
    msgbox as msg_box,
    scratch_path as get_temp_dir,
    yesno_popup_ask as ask_yn,
)
from core.zerr import zerr


def check_for_last_cache(gui: bool = False) -> Optional[str]:
    try:
        temp_dir = get_temp_dir()
        cache_file = get_newest_file(temp_dir, "pkl")
        if cache_file is None:
            return None
        else:
            if gui:
                response = ask_yn(f"Found cache file: {cache_file}\nUse it?")
            else:
                response = ask_q(
                    f"Found cache file: {cache_file}\nUse it? (y/n): "
                )
            if response:
                return cache_file
            else:
                return None
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def create_dir(dir_path: str) -> Tuple[bool, Optional[str]]:
    try:
        if not path.exists(dir_path):
            os.makedirs(dir_path)
        log(f"Created directory: {dir_path}", success=True)
        return True, None
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return False, error_info


def dir_check(path: str, create: bool = False) -> Tuple[bool, Optional[str]]:
    return filer_check(path, "dir", create)


def file_check(path: str) -> Tuple[bool, Optional[str]]:
    return filer_check(path, "file")


def filer_check(
    itempath: str, itemtype: str = "file", create: bool = False
) -> Tuple[bool, Optional[str]]:
    type_name = itemtype.capitalize()
    try:
        if itemtype == "file":
            if not path.exists(itempath):
                return False, f"{type_name} does not exist: {itempath}"
            if not path.isfile(itempath):
                return False, f"Path is not a file: {itempath}"
        else:
            if not path.exists(itempath):
                if create:
                    create_result = create_dir(itempath)
                    if create_result[0]:
                        return True, None
                    else:
                        raise Exception(create_result[1])
                else:
                    raise Exception(f"{type_name} does not exist: {itempath}")
            if not path.isdir(itempath):
                raise Exception(f"Path is not a directory: {itempath}")
        if not os.access(itempath, os.R_OK):
            raise Exception(f"{type_name} is not readable: {itempath}")
        if not os.access(itempath, os.W_OK):
            raise Exception(f"{type_name} is not writable: {itempath}")
        return True, None
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return False, error_info


def generate_cache_file(timestamp: str) -> str:
    try:
        temp_dir = get_temp_dir()
        cache_path = os.path.join(temp_dir, f"{timestamp}_cache.pkl")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        return cache_path
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_file_path(
    filename: str,
    file_type: str,
    gui: bool = False,
    verbose: bool = False,
) -> str:
    try:
        types_dict = file_types_dict()
        if file_type == "extractable":
            file_types = [
                (
                    "Audio/Videos Files",
                    " ".join(types_dict["ffmpeg_a"] + types_dict["ffmpeg_v"]),
                ),
                ("Audio Files", " ".join(types_dict["ffmpeg_a"])),
                ("Video Files", " ".join(types_dict["ffmpeg_v"])),
            ]
        elif file_type == "audio":
            file_types = [("Audio Files", " ".join(types_dict["ffmpeg_a"]))]
        elif file_type == "video":
            file_types = [("Video Files", " ".join(types_dict["ffmpeg_v"]))]
        else:
            file_types = [("All Files", "*.*")]
        file_path = (
            filename if filename is not None or filename != "" else None
        )

        if file_path is None or file_path == "":
            prompt = f"Enter the path to the {file_type} file: "
            if gui:
                file_path = ask_box(file_types, "open")
            else:
                file_path = str(ask_q(prompt))

        if file_path is None or file_path == "":
            error = f"No {file_type} file selected"
            if gui and verbose:
                msg_box("Error", error)
            else:
                print(error)
            raise Exception(error)
        else:
            file_path = file_path.lower()

        if not file_check(file_path)[0]:
            error = file_check(file_path)[1]
            if gui and verbose:
                msg_box("Error", error)
            else:
                print(error)
            raise Exception(error)
        else:
            file_path = os.path.abspath(file_path)

        return file_path

    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_folder_path(filepath: str) -> Optional[str]:
    directory_path = os.path.dirname(filepath)
    if dir_check(directory_path)[0]:
        return directory_path
    else:
        error_info = f"{dir_check(directory_path)[1]}:" f"[{directory_path}]"
        log(error_info, "ERROR")
        return None


def get_newest_file(folderpath: str, fileext: str) -> Optional[str]:
    try:
        extension = (
            fileext if fileext.startswith(".") else f".{fileext.lstrip('.')}"
        )
        files = glob.glob(f"{folderpath}/*{extension}")
        if len(files) == 0 or files is None or not files:
            return None
        else:
            return max(files, key=os.path.getctime)
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_output_folder(ogfilepath: str, outputfolderarg: Optional[str]) -> str:
    try:
        if outputfolderarg is not None or outputfolderarg != "":
            of_result = dir_check(str(outputfolderarg))
            if of_result[0]:
                return str(outputfolderarg)
        output_folder = str(get_folder_path(ogfilepath))
        ogoutfold_result = dir_check(output_folder)
        if ogoutfold_result[0]:
            return output_folder
        else:
            error_info = f"{ogoutfold_result[1]}: [{output_folder}]"
            log(error_info, "ERROR")
            raise Exception(error_info)
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def get_output_path(
    ogfilepath: str, type: int = 0, outputfolderarg: Optional[str] = None
) -> str:
    try:
        output_folder = get_output_folder(ogfilepath, outputfolderarg)

        if type == 0 or type == 1:
            output_path = os.path.join(
                output_folder, f"{os.path.basename(ogfilepath)}.txt"
            )
        elif type == 2:
            output_path = os.path.join(
                output_folder, f"{os.path.basename(ogfilepath)}.srt"
            )
        else:
            raise Exception(f"Unsupported output type: {type}")
        return output_path
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        raise Exception(error_info)


def scratch_cleanup() -> Tuple[bool, Optional[str]]:
    try:
        temp_dir = get_temp_dir()
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            if not os.path.exists(temp_dir):
                log("Scratch directory cleaned up", success=True)
                return True, None
            else:
                raise Exception("Scratch directory cleanup failed")
        return True, None
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return False, error_info


def write_to_file_with_ask(
    data,
    default_location: Optional[str] = None,
    extension: str = ".txt",
    gui: bool = False,
    verbose: bool = False,
) -> Tuple[bool, Optional[str]]:
    try:
        if default_location is None or default_location == "":
            default_location = os.getcwd()
        if gui and verbose:
            if extension == ".txt":
                output_file_path = ask_box(
                    [("Text Files", "*.txt")],
                    "save",
                    default_location,
                )
            elif extension == ".srt":
                output_file_path = ask_box(
                    [("SRT Files", "*.srt")],
                    "save",
                    default_location,
                )
            else:
                output_file_path = ask_box(
                    [("All Files", "*.*")],
                    "save",
                    default_location,
                )
        else:
            if verbose:
                output_file_path = ask_q("Enter the path to the output file: ")
            else:
                output_file_path = ""
        if output_file_path is None or output_file_path == "":
            output_file_path = default_location
        if output_file_path is None or output_file_path == "":
            if gui and verbose:
                msg_box("Error", "No output location selected")
            else:
                print("No output location selected")
            raise Exception("No output location selected")
        output_file_path = str(output_file_path)
        if not output_file_path.endswith(extension):
            output_file_path += extension
        with open(output_file_path, "w") as f:
            f.write(data)
        return True, None
    except Exception as e:
        error_info = zerr(e)
        log(error_info, "ERROR")
        return False, error_info
