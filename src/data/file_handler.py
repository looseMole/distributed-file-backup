import os

import csv

import requests

class file_handler:
    uploaded_files = {}

    def __init__(self):
        self.load_links()

    def load_links(self):
        try:
            with open(".\\uploaded_files.csv", 'r') as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if len(line) > 0:
                        line_parts = line[0].split('|')
                        self.uploaded_files[line_parts[0]] = line_parts[1]
                f.close()
            print("Following uploads loaded:")
            print(self.uploaded_files.__str__())

        except FileNotFoundError:
            print("No previous uploads found")

    def save_links(self):
        with open(".\\uploaded_files.csv", 'w') as f:
            writer = csv.writer(f)
            keys = list(self.uploaded_files.keys())
            for i in range(len(self.uploaded_files)):
                key = keys[i]
                writer.writerow([key + "|" + self.uploaded_files[key]])
            f.close()

    def upload_file(self, filepath, server):
        switcher = {
            "anonfiles": "https://api.anonfiles.com/upload",
            "filechan": "https://api.filechan.org/upload",
            "letsupload": "https://api.letsupload.cc/upload",
            "bayfiles": "https://api.bayfiles.com/upload",
            "openload": "https://api.openload.cc/upload",
            "megaupload": "https://api.megaupload.nz/upload",
            "shareonline": "https://api.share-online.is/upload",
            "vshare": "https://api.vshare.is/upload",
            "hotfile": "https://api.hotfile.io/upload",
            "rapidshare": "https://api.rapidshare.nu/upload",
            "lolabits": "https://api.lolabits.se/upload",
            "upvid": "https://api.upvid.cc/upload",
        }

        url = switcher.get(server, "")
        if url == "":
            print("Invalid server.")
            return False

        with open(filepath, "rb") as a_file:
            filename = os.path.basename(filepath)
            _files = {"file": (filename, a_file)}
            r = requests.post(url=url, files=_files).json()
            print(r)  # Print response from server, received as a JSON.

        if r["status"]:
            self.uploaded_files[filename] = r["data"]["file"]["url"]["full"]
            return True
        else:
            return False

    def download_file(self, link):
        pass

    def check_files(self, links):
        pass
