# MTL Shorts

MTL Shorts is a Python script designed to render YouTube Shorts from newsletters fetched via an API. The script processes the newsletter data, generates a video with text and audio, and saves it to a specified output directory.

## Features
- Fetch newsletters from a specified API endpoint.
- Generate video clips with text and audio narration.
- Customize output with various command-line options.

## Requirements
- Python 3.12 or later
- Required Python packages listed in `requirements.txt`
- ImageMagick for text rendering in videos

## Setup
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd mtl-shorts
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ImageMagick**
   ```bash
   brew install imagemagick
   ```

5. **Set Environment Variables**
   Create a `.env` file in the project root with the following content:
   ```
   BASIC_USER=your_username
   BASIC_PASS=your_password
   API_URL=https://zaiks.smartfeed.media/api/v1/newsletters/
   ```

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
This project is licensed under the MIT License.
# mtl-python-video-shorts-generator-poc
