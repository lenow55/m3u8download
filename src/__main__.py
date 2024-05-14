import logging
import os
import sys
from functools import partial
from argparse import ArgumentParser
from typing import Callable
import concurrent.futures as concurrent_f

import requests
from tqdm import tqdm

fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

shell_handler = logging.StreamHandler(sys.stdout)
shell_handler.setLevel(logging.INFO)
shell_handler.setFormatter(fmt)

logging.basicConfig(level=logging.INFO, handlers=[shell_handler])
logger = logging.getLogger(__name__)

parser: ArgumentParser = ArgumentParser(prog="download_m3u8_tss.py")
parser.add_argument(
    "-u",
    "--url",
    type=str,
    required=True,
    help="url с по которому лежит файл",
)


def update_pbar(pbar, count):
    pbar.update(count)


def processing_download_video_ts_files(url: str, filename: str, callback: Callable):
    try:
        response = requests.get(
            url,
            timeout=30.0,
        )
        if response.status_code == 200:
            with open(filename, "wb") as downloaded_file:
                downloaded_file.write(response.content)

    except Exception as e:
        logger.error(e)
    finally:
        callback(1)

    return


def main():
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    args = parser.parse_args()

    url_parts = args.url.split("/")
    parent_url = "/".join(url_parts[:-1])
    # get m3u8
    try:
        response = requests.get(args.url)
        if response.status_code == 200:
            with open("index.m3u8", "wb") as downloaded_file:
                downloaded_file.write(response.content)
    except requests.RequestException as e:
        raise e

    playlist_urls = []
    with open("index.m3u8", "r") as index_file:
        with open(os.path.join("./tmp", "filelist.txt"), "w") as out_index_file:
            for line in index_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    file_url = (
                        f"{parent_url}/{line}"
                        if parent_url and not line.startswith(("http://", "https://"))
                        else line
                    )
                    logger.debug(f"Playlist File url: {file_url}")
                    out_index_file.write(f"file '{line}'\n")
                    playlist_urls.append(
                        {"filename": os.path.join("tmp", line), "url": file_url}
                    )

    pbar = tqdm(total=len(playlist_urls))
    update_video_pbar = partial(update_pbar, pbar)

    with concurrent_f.ThreadPoolExecutor(max_workers=24) as executor:
        for info in playlist_urls:
            executor.submit(
                processing_download_video_ts_files,
                info["url"],
                info["filename"],
                update_video_pbar,
            )

    pbar.close()


if __name__ == "__main__":
    main()
