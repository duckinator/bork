from pathlib import Path
from urllib.request import urlopen


def download_assets(asset_list, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    for asset in asset_list:
        name = asset['name']
        url = asset['url']
        path = directory / name

        contents = urlopen(url).read()

        path.write_bytes(contents)
        print(str(path))
