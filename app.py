import argparse
import os
import pickle
import srt
import moviepy.editor as mp
import whisper_timestamped as whisper


from datetime import datetime, timedelta
from pydub import AudioSegment
from tkinter import Tk, filedialog, messagebox


whisper_supported_audio_file_types = [
    "*.wav",
    "*.mp3",
    "*.m4a",
    "*.ogg",
    "*.flac",
]
moviepy_supported_video_file_types = [
    "*.mp4",
    "*.avi",
    "*.mov",
    "*.mpg",
    "*.ogv",
]

ffmpeg_audio_file_types = [
    "*.3g2",
    "*.3gp",
    "*.aac",
    "*.ac3",
    "*.flac",
    "*.m4a",
    "*.m4b",
    "*.m4r",
    "*.mka",
    "*.mp3",
    "*.mp4",
    "*.ogg",
    "*.oga",
    "*.opus",
    "*.ra",
    "*.ram",
    "*.wav",
    "*.wma",
]


ffmpeg_video_file_types = [
    "*.3g2",
    "*.3gp",
    "*.asf",
    "*.avi",
    "*.dv",
    "*.f4v",
    "*.flv",
    "*.m2ts",
    "*.m4v",
    "*.mkv",
    "*.mov",
    "*.mp4",
    "*.mpeg",
    "*.mpg",
    "*.mts",
    "*.mxf",
    "*.ogv",
    "*.rm",
    "*.rmvb",
    "*.ts",
    "*.vob",
    "*.webm",
    "*.wmv",
]


def main():
    # TODO: Add check for ffmpeg if not exist download
    # TODO: Break main down into multiple functions
    # TODO: Add arguments into main and move argparse code to __main__
    # TODO: Add support converting languages (from audio source to other)
    # TODO: Modularize code
    # TODO: Add my logger function for debugging and logging

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

    if os.name == "posix" and os.environ.get("DISPLAY", "") == "":
        gui = False
    else:
        gui = True

    file_type = "video"
    audio_path = None
    converted_audio_path = None
    converted_file_path = None

    if gui:
        root = Tk()
        root.withdraw()

    if args.file:
        file_path = args.file
    elif gui:
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Audio files", " ".join(ffmpeg_audio_file_types)),
                ("Video files", " ".join(ffmpeg_video_file_types)),
            ]
        )
    else:
        file_path = input("Enter the path to the video file: ")

    if file_path is None or file_path == "":
        if gui and args.verbose:
            messagebox.showerror("Error", "No file selected")
        else:
            print("No file selected")
        return
    else:
        file_path = file_path.lower()

    if not os.path.exists(file_path):
        if gui and args.verbose:
            messagebox.showerror("Error", "File does not exist")
        else:
            print("File does not exist")
        return

    if file_path.endswith(tuple(ffmpeg_video_file_types)):
        file_type = "video"
        if not file_path.endswith(tuple(moviepy_supported_video_file_types)):
            try:
                clip = mp.VideoFileClip(file_path)
                converted_file_path = f"{timestamp}_converted.mp4"
                clip.write_videofile(converted_file_path)
                file_path = converted_file_path
            except Exception as e:
                if gui and args.verbose:
                    messagebox.showerror("Error", str(e))
                else:
                    print(str(e))
                return
        else:
            clip = mp.VideoFileClip(file_path)
            audio_path = f"{timestamp}_audio.wav"
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if clip.audio is not None:
                clip.audio.write_audiofile(audio_path)
            else:
                if gui and args.verbose:
                    messagebox.showerror(
                        "Error", "The video file does not contain audio"
                    )
                else:
                    print("The video file does not contain audio")
                return
    else:
        file_type = "audio"
        if not file_path.endswith(tuple(whisper_supported_audio_file_types)):
            try:
                audio = AudioSegment.from_file(file_path)
                converted_audio_path = f"{timestamp}_audio_converted.wav"
                audio.export(converted_audio_path, format="wav")
                audio_path = converted_audio_path
            except Exception as e:
                if gui and args.verbose:
                    messagebox.showerror("Error", str(e))
                else:
                    print(str(e))
                return
        else:
            audio_path = file_path

    if audio_path is None or audio_path == "":
        if gui and args.verbose:
            messagebox.showerror("Error", "No audio file selected")
        else:
            print("No audio file selected")
        return

    if not os.path.exists(audio_path):
        if gui and args.verbose:
            messagebox.showerror("Error", "Audio file does not exist")
        else:
            print("Audio file does not exist")
        return

    cache_file = f"{timestamp}_cache.pkl"
    result = None

    if not os.path.exists(cache_file):
        audio = whisper.load_audio(audio_path)
        model = whisper.load_model(args.model)
        result = whisper.transcribe(model, audio, language=args.language)

        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
    else:
        with open(cache_file, "rb") as f:
            result = pickle.load(f)
    second_output_format = ""
    if args.type > 2 or args.type < 0 or args.type is None:
        if gui:
            output_format = messagebox.askquestion(
                "Output format",
                "Do you want the transcription in .srt format?",
                icon="warning",
            )
        else:
            output_format = input(
                "Do you want the transcription in .srt format? (yes/no): "
            )
            if output_format.lower().startswith("y"):
                output_format = "yes"
                args.type = 2
            else:
                output_format = "no"
                if gui:
                    second_output_format = messagebox.askquestion(
                        "Output format",
                        "Do you want the transcription with timestamps?",
                        icon="warning",
                    )
                else:
                    second_output_format = input(
                        "Do you want the transcription "
                        "with timestamps? (yes/no): "
                    )
                    if second_output_format.lower().startswith("y"):
                        second_output_format = "yes"
                        args.type = 1
                    else:
                        second_output_format = "no"
                        args.type = 0
        if output_format.lower() == "yes":
            args.type = 2
        elif second_output_format.lower() == "yes":
            args.type = 1
        else:
            args.type = 0

    output_file_path = None

    if args.language is None or args.language == "":
        language = "en"
    else:
        language = args.language

    if args.outputfolder:
        output_file_path = os.path.join(
            args.outputfolder, os.path.splitext(os.path.basename(file_path))[0]
        )

    if args.type == 2:
        subs = []
        for i, seg in enumerate(result["segments"]):
            start_time = timedelta(seconds=seg["start"])
            end_time = timedelta(seconds=seg["end"])
            content = seg["text"]
            # TODO: add support for translating to other languages
            #       if the extracted language is not english
            subs.append(srt.Subtitle(i, start_time, end_time, content))

        srt_content = srt.compose(subs)

        if gui and args.verbose:
            output_file_path = filedialog.asksaveasfilename(
                defaultextension=".srt"
            )
        else:
            if args.verbose:
                output_file_path = input("Enter the path to the output file: ")
            else:
                output_file_path = ""
        if output_file_path is None or output_file_path == "":
            output_file_path = os.path.splitext(file_path)[0]
        if output_file_path is None or output_file_path == "":
            if gui and args.verbose:
                messagebox.showerror("Error", "No output location selected")
            else:
                print("No output location selected")
            return
        if not output_file_path.endswith(".srt"):
            output_file_path += ".srt"

        if language is not None or language != "":
            output_file_path = (
                output_file_path[: -len(os.path.splitext(output_file_path)[1])]
                + f".{language}"  # noqa
                + os.path.splitext(output_file_path)[1]  # noqa
            )

        with open(output_file_path, "w") as f:
            f.write(srt_content)
    else:
        if gui and args.verbose:
            output_file_path = filedialog.asksaveasfilename(
                defaultextension=".txt"
            )
        else:
            if args.verbose:
                output_file_path = input("Enter the path to the output file: ")
            else:
                output_file_path = ""
        if output_file_path is None or output_file_path == "":
            output_file_path = os.path.splitext(file_path)[0]
        if output_file_path is None or output_file_path == "":
            if gui and args.verbose:
                messagebox.showerror("Error", "No output location selected")
            else:
                print("No output location selected")
            return
        if not output_file_path.endswith(".txt"):
            output_file_path += ".txt"
        if args.type == 1:
            with open(output_file_path, "w") as f:
                for seg in result["segments"]:
                    f.write(
                        f'{str(timedelta(seconds=seg["start"]))}'
                        " --> "
                        f'{str(timedelta(seconds=seg["end"]))}'
                        "\n"
                    )
                    f.write(seg["text"] + "\n")
        else:
            with open(output_file_path, "w") as f:
                for seg in result["segments"]:
                    f.write(seg["text"] + "\n")

    if os.path.exists(output_file_path):
        if file_type == "video":
            os.remove(audio_path)
        if converted_file_path is not None:
            os.remove(converted_file_path)
        if converted_audio_path is not None:
            os.remove(converted_audio_path)
        if os.path.exists(cache_file):
            os.remove(cache_file)
        if gui and args.verbose:
            messagebox.showinfo("Success", "Transcription complete!")
        else:
            print("Transcription complete!")
    else:
        if gui and args.verbose:
            messagebox.showerror(
                "Error", "Something went wrong while saving the file"
            )
        else:
            print("Something went wrong while saving the file")
    return


if __name__ == "__main__":
    main()
