import asyncio
import json
import os
import time
import aiohttp
import shutil
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    'Referer': 'https://www.curseforge.com/minecraft/mc-mods/cloth-config/download/5834708',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0, i',
} # i love curlconverter.com

class Logger:
    """
    Logger class
    """
    def __init__(self):
        self.logfile = open("last.log", "w")
        self.logfile.write("CurseDL\n")

    def __raw(self, message):
        print(message, end="", flush=True)
        self.logfile.write(message)
        self.logfile.flush()

    def log(self, message, prefix="[MAIN]", end="\n"):
        self.__raw(prefix+" "+message+end)

def get_filename(response: aiohttp.ClientResponse) -> str:
    """
    Get the filename from a given response.
    """
    return response.url.path.split("/")[-1]
async def download(url: str, path: str, logger: Logger) -> None:
    """
    Download a file from a given URL and save it to a given path.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logger.log(f"Downloading {url}", prefix="[DL]")
                filename = get_filename(response)
                with open(path+filename, "wb") as f:
                    while True:
                        data = await response.content.read(1024)
                        if not data:
                            break
                        f.write(data)
        except Exception as e:
            logger.log(f"Failed to download {url}", prefix="[DL]")
            logger.log(f"Error: {e}", prefix="[ERR]")
            return

def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs

async def main() -> None:
    logger = Logger()
    print(r"""
                              _ _ 
  ___ _   _ _ __ ___  ___  __| | |
 / __| | | | '__/ __|/ _ \/ _` | |
| (__| |_| | |  \__ \  __/ (_| | |
 \___|\__,_|_|  |___/\___|\__,_|_|
                                  
""")
    logger.log("Reading manifest...")
    with open("modpack/manifest.json", "r") as f:
        manifest = json.load(f)
        mc = manifest["minecraft"]
        version = mc["version"]
        modLoaders = mc["modLoaders"]
        for modLoader in modLoaders:
            if modLoader["primary"]:
                loader = modLoader["id"]
                logger.log(f"Primary ModLoader: {loader}\tVersion: {version}")
                break
        logger.log(f"Downloading modpack {manifest['name']} v{manifest['version']} by {manifest['author']}")
        mods = manifest["files"]

        modTasks = []
        os.makedirs("output/mods/", exist_ok=True)

        for mod in mods:
            pId = mod["projectID"]
            fId = mod["fileID"]
            required = mod["required"] # Not used (currently)
            modTasks.append(download(f"https://www.curseforge.com/api/v1/mods/{pId}/files/{fId}/download", f"output/mods/", logger))

        # Downloading 5 mods in parallel at one time
        work = split(modTasks, 5)
        for batch in work:
            await asyncio.gather(*batch)

        logger.log(f"Mods downloaded to output/mods/")
        logger.log(f"Moving overrides...")
        src_path = Path("modpack/overrides/")
        dest_path = Path("output/")
        for file in src_path.glob("*"):
            logger.log(str(file), prefix="[MAIN] +")
            if file.is_dir():
                shutil.copytree(file, dest_path.joinpath(file.name), dirs_exist_ok=True)
            else:
                shutil.copy(file, dest_path)
        logger.log(f"Overrides moved to output/")
asyncio.run(main())