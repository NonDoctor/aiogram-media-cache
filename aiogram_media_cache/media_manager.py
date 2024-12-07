import os
import pickle
import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import FSInputFile


class MediaManager:
    """
    A class to manage media files for Telegram bots using aiogram.
    It uploads files to Telegram servers, caches their file_id to avoid
    re-uploading, and provides an easy interface to access them.
    """

    def __init__(
        self,
        bot: Bot,
        upload_id: int,
        assets_dir: str,
        cache_file: str = "media_cache.pkl",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the MediaManager.

        :param bot: An instance of the aiogram Bot.
        :param upload_id: ID of the chat/user where media files will be uploaded.
        :param assets_dir: Path to the directory containing media files.
        :param cache_file: Name of the file to store file_id cache.
        """
        self.logger = logger or logging.getLogger("aiogram_media_cache")
        self.bot = bot
        self.upload_id = upload_id
        self.cache_file = cache_file
        self.assets_dir = assets_dir
        self.media_cache = self._load_cache()

    def _load_cache(self):
        """
        Load file_id cache from a file.
        If the cache file doesn't exist, returns an empty dictionary.

        :return: A dictionary with filenames as keys and file_ids as values.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    self.logger.info("Cache successfully loaded from file.")
                    return pickle.load(f)
            except Exception as e:
                self.logger.error(f"Error while loading cache: {e}")
                return {}
        self.logger.warning("Cache file not found. Creating a new cache.")
        return {}

    def _save_cache(self):
        """
        Save the current state of the file_id cache to a file.
        """
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.media_cache, f)
            self.logger.info("Cache successfully saved to file.")
        except Exception as e:
            self.logger.error(f"Error while saving cache: {e}")

    async def upload_assets(self):
        """
        Upload all files from the assets_dir to Telegram and cache their file_ids.
        """
        if not os.path.exists(self.assets_dir) or not os.path.isdir(self.assets_dir):
            self.logger.error(
                f"Directory '{self.assets_dir}' does not exist or is not a folder."
            )
            return

        for filename in os.listdir(self.assets_dir):
            filepath = os.path.join(self.assets_dir, filename)
            if os.path.isfile(filepath):
                if filename not in self.media_cache:
                    try:
                        self.logger.info(f"Uploading file '{filename}'...")
                        file_id = await self._upload_file(filepath)
                        self.media_cache[filename] = file_id
                        self.logger.info(
                            f"File '{filename}' uploaded and cached successfully."
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Error while uploading file '{filename}': {e}"
                        )
        self._save_cache()

    async def _upload_file(self, filepath):
        """
        Upload a single file to Telegram and retrieve its file_id.

        :param filepath: Full path to the file.
        :return: file_id of the uploaded file.
        """
        file = FSInputFile(filepath)
        file_type = os.path.splitext(filepath)[1].lower()

        try:
            if file_type in [".jpg", ".jpeg", ".png"]:
                # Upload image
                message = await self.bot.send_photo(chat_id=self.upload_id, photo=file)
                return message.photo[-1].file_id
            elif file_type in [".mp4", ".mp3"]:
                # Upload video
                message = await self.bot.send_video(chat_id=self.upload_id, video=file)
                return message.video.file_id
            else:
                raise ValueError(f"Unsupported file type: '{file_type}'.")
        except Exception as e:
            self.logger.error(f"Error while uploading file '{filepath}': {e}")
            raise

    def get_file_id(self, filename):
        """
        Retrieve the file_id for a given filename.

        :param filename: Name of the file.
        :return: file_id if the file is cached, otherwise None.
        """
        file_id = self.media_cache.get(filename)
        if file_id:
            self.logger.info(f"file_id for '{filename}' found in cache.")
        else:
            self.logger.warning(f"file_id for '{filename}' not found in cache.")
        return file_id

    def clear_cache(self):
        """
        Clear the cache (both in memory and on disk).
        """
        self.media_cache = {}
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                self.logger.info("Cache file successfully removed from disk.")
        except Exception as e:
            self.logger.error(f"Error while removing cache file: {e}")
        self.logger.info("Cache in memory cleared.")
