# aiogram-media-cache

`aiogram-media-cache` is a Python package designed to simplify media file management in Telegram bots using the `aiogram` framework. It uploads media files (images, videos, etc.) to Telegram servers and caches their `file_id` to avoid redundant uploads in the future. This allows for faster and more efficient handling of media files.

## Features

- Uploads images, videos, and other supported media types to Telegram servers.
- Caches `file_id`s to avoid uploading the same file multiple times.
- Easy-to-use interface for managing and accessing cached media.

## Installation

### Install using poetry
```
poetry add git+https://github.com/NonDoctor/aiogram-media-cache.git
```

### Install using pip
```
pip install git+https://github.com/NonDoctor/aiogram-media-cache.git
```

## Example
```python
import asyncio
from aiogram import Bot
from aiogram-media-cache import MediaManager  # Import the MediaManager class

# Initialize bot with your token
bot = Bot(token="YOUR_BOT_TOKEN")

# Path to the directory containing your media files
assets_dir = "path/to/your/assets"

# The user or chat ID through which media will be uploaded (can be your own ID)
upload_id = 123456789  # Replace with the actual ID

# Create an instance of the MediaManager
media_manager = MediaManager(
    bot=bot,
    upload_id=upload_id,
    assets_dir=assets_dir,
    cache_dir="__pycache__"  # Optional: you can specify the cache directory
)

# Upload media files and cache their file_ids
async def upload_media():
    await media_manager.upload_assets()

# Run the upload process
asyncio.run(upload_media())

# Get file_id for a specific file (retrieved from cache)
file_id = media_manager.get_file_id("image.jpg")
print(file_id)
```
