# TranscriptGen

TranscriptGen is an application for transcribing audio and video files. Transcription output is .txt or .srt. Most audio and video formats supported (with ffmpeg).

## Author


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Supported File Types](#supported-file-types)
- [Contributing](#contributing)
- [License](#license)

## Installation

Clone this repository and navigate to the project folder. Then run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the program from the command line:

```bash
python main.py
```

(Optional) Run the program with arguments:

```bash
python main.py -f <file_path> -l <language> -m <model> -o <output_folder> -t <output_type> -v <verbose>
```

- `-f, --file`: Path to the video/audio file
- `-l, --language`: Language code of the audio file (default: en)
- `-m, --model`: Whisper Model name (default: base)
- `-o, --outputfolder`: Output folder for the transcription file
- `-t, --type`: The output format (0: transcript only, 1: transcript with time, 2: .srt file)
- `-v, --verbose`: Verbose output (0: off, 1: on)


## Supported File Types

### Audio
- 3g2
- 3gp
- aac
- ac3
- flac
- m4a
- m4b
- m4r
- mka
- mp3
- mp4
- ogg
- oga
- opus
- ra
- ram
- wav
- wma

### Video
- 3g2
- 3gp
- asf
- avi
- dv
- f4v
- flv
- m2ts
- m4v
- mkv
- mov
- mp4
- mpeg
- mpg
- mts
- mxf
- ogv
- rm
- rmvb
- ts
- vob
- webm
- wmv

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License.

## Contact

For any queries or concerns, please contact Geoff Clark at geoff @ clarktribegames . com.
