# MTL Shorts

MTL Shorts is a Python script designed to render YouTube Shorts from newsletters fetched via an API. The script processes the newsletter data, generates a video with text and audio, and saves it to a specified output directory. This tool is just a simple Proof of Concept to show how we can generate video by using PyMovie library.

## Features

- Fetch newsletters from a specified API endpoint.
- Generate video clips with text and audio narration.
- Customize output with various command-line options.

## Requirements

- Python 3.12 or later
- Required Python packages listed in `requirements.txt`
- ImageMagick for text rendering in videos

## Installation

### 1. Clone the Repository

Clone the repository to your local machine using the following command:
```bash
git clone https://github.com/musictechlab/mtl-python-video-shorts-generator-poc.git
cd mtl-shorts
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment to manage dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the necessary Python packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Install ImageMagick

ImageMagick is required for rendering text in videos. Install it using Homebrew:

```bash
brew install imagemagick
```

### 5. Configure Environment Variables

Create a `.env` file in the project root with the following content:
```

BASIC_USER=your_username
BASIC_PASS=your_password
API_URL=https://zaiks.smartfeed.media/api/v1/newsletters/
```

Replace `your_username` and `your_password` with your actual API credentials.

## Usage

Run the script with the desired options:
```bash

python3 app.py --limit 1 --out output_directory --prefix short_prefix
```

- `--limit`: Number of items to render (default is 1).
- `--out`: Output directory for the video files.
- `--prefix`: Prefix for the output filenames.

## Troubleshooting

- Ensure ImageMagick is installed and accessible in your PATH.
- Check that all required environment variables are set correctly.

## License

MIT License

Copyright (c) 2025 MusicTech Lab Sp. z o.o

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Links

MusicTech Lab - Rockstars Developers dedicated to the The Music Industry

- [Website](https://www.musictechlab.io)
- [LinkedIn](https://linkedin.com/company/musictechlab/)
- [Youtube](https://www.youtube.com/@musictechlab-io)