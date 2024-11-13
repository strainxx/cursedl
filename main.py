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
    # 'Cookie': 'cf_cookieBarHandled=true; Unique_ID_v2=8e99d8b1ad2e461ab808f5c1aadf5621; CobaltSession=eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..keTqvSHcrNVDxRqjMq5XMw.g26rp0MyDG1giAIPz97wvDMs5ZOuhpWHd4NcME3ZtDOu6ua5__LDoXO42H9x12Eh.0QuRi-l-EGPcLd9lPz5J2Q; User=User%3DUserID%3D109413140%26UserName%3Deager_minsky49%26UserEmail%3Dyarik.chotkii%40gmail.com%26UserAvatar%3Dundefined; SiteUserToken=s%3AeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEwOTQxMzE0MCIsInNlc3Npb24iOiIyNDNlODg1YWU1MzE0M2E5YjdhMjMwZjcwYzU3NGU2MCIsImlhdCI6MTczMTE1MTIxOCwiZXhwIjoxNzMyMzYwODE4LCJpc3MiOiJjdXJzZWZvcmdlLmNvbSJ9.RdRBDLJBkyptH4YVg3XiDGjSl-weTkbjY8VfGhWf-PU.13a5HshpTBKJdXo6Fi1tPsLVsK6hangpxsAWU2wuTjA; Preferences.TimeZoneID=87; __cf_bm=Vhzl757rMZ6qH70Ku8xJLx079xGlc.ZCZXE6h.wnc2o-1731506181-1.0.1.1-1cm.K5NVv82SMdljIiyT27.5bzfhBwwkUaZJSbgC0BGCNBtRE4s.67llELG348UTs4d9fQIifo22mtkDvKhna_mxODSaHO5CUQJLSXB9pOc',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0, i',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

class Logger:
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
    return response.url.path.split("/")[-1]
async def download(url: str, path: str, logger: Logger) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            logger.log(f"Downloading {url}", prefix="[DL]")
            filename = get_filename(response)
            with open(path+filename, "wb") as f:
                while True:
                    data = await response.content.read(1024)
                    if not data:
                        break
                    f.write(data)


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
            required = mod["required"]
            modTasks.append(download(f"https://www.curseforge.com/api/v1/mods/{pId}/files/{fId}/download", f"output/mods/", logger))

        # await asyncio.gather(*modTasks)
        logger.log(f"Mods downloaded to output/mods/")
        logger.log(f"Moving overrides...")
        # os.makedirs("output/overrides/", exist_ok=True)
        dest_path = Path("output/overrides/")
        src_path = Path("modpack/")
        # for file in src_path.glob("*"):
        #     print(file)
        #     if file.is_dir():
        #         shutil.copytree(file, src_path)
        #     else:
        #         shutil.copy(file, dest_path)
        logger.log(f"Overrides moved to output/")
asyncio.run(main())