import os
import csv
import hashlib
import requests

class file_handler:
    uploaded_files = {}
    server_switcher = {
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

    def __init__(self):
        self.are_servers_up()
        self.load_links()

    # Loads information about previously uploaded files, from CSV-file.
    def load_links(self):
        try:
            with open(".\\uploaded_files.csv", 'r') as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if len(line) > 0:
                        line_parts = line[0].split('|')
                        self.uploaded_files[line_parts[0]] = []
                        i = 1
                        # Info loaded in a loop, as files can have an arbitrary amount of download links.
                        while i < len(line_parts):
                            self.uploaded_files[line_parts[0]].append(line_parts[i])
                            i += 1
                f.close()
            print("Following uploads loaded:")
            print(self.uploaded_files.__str__())

        except FileNotFoundError:
            print("No previous uploads found")

    # Checks up-status of the servers specified in server_switcher. Prints result
    def are_servers_up(self):
        print("Checking servers' status...")

        servers_up = 0
        for key in self.server_switcher.keys():
            url = self.server_switcher.get(key)
            url = url.removesuffix("/upload")
            r = requests.get(url)
            if r.status_code == 200:  # Response 200 is optimal
                servers_up += 1
            else:
                print(key + " status: Not optimal (Response: " + str(r.status_code) + ")")
            if servers_up == len(self.server_switcher.keys()):
                print("All servers are up")

    # Saves information from uploaded_files to a CSV-file.
    def save_links(self):
        with open(".\\uploaded_files.csv", 'w') as f:
            writer = csv.writer(f)
            keys = list(self.uploaded_files.keys())
            for i in range(len(self.uploaded_files)):
                key = keys[i]
                file_string = key
                for i in range(len(self.uploaded_files[key])):
                    file_string += "|" + self.uploaded_files[key][i]

                writer.writerow([file_string])
            f.close()

    # Returns hash of the file corresponding to the given filepath.
    def get_file_hash(self, filepath):
        BUF_SIZE = 65536  # Amount of bytes to process at a time, preventing huge memory usage.
        sha1 = hashlib.sha1()

        with open(filepath, "rb") as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    # Uploads file to specified server, then calls save_links().
    def upload_file(self, filepath, server):
        url = self.server_switcher.get(server, "")
        if url == "":
            print("Invalid server.")
            return False

        # TODO: Create exception handling for invalid filepath.
        with open(filepath, "rb") as a_file:
            filename = os.path.basename(filepath)
            _files = {"file": (filename, a_file)}
            r = requests.post(url=url, files=_files).json()
            print(r)  # Print response from server, received as a JSON.

        if r["status"]:
            file_hash = self.get_file_hash(filepath)
            download_url = r["data"]["file"]["url"]["full"]
            # If a file with this SHA1-hash has already been uploaded, append the download to that file.
            if file_hash in self.uploaded_files:
                self.uploaded_files[file_hash].append(download_url)
            else:
                self.uploaded_files[file_hash] = [filename, download_url]
            self.save_links()
            return True
        else:
            return False

    def download_file(self, file_name, url):
        if not os.path.exists(".\\downloads"):
            os.makedirs(".\\downloads")

        # Get direct download link.
        r = requests.get(url)
        direct_url_start = r.text.find("https://cdn")
        direct_url_end = r.text.find("\"", direct_url_start)
        direct_url = r.text[direct_url_start:direct_url_end]

        # Download file
        file_bytes = requests.get(direct_url)
        filepath = ".\\downloads\\" + file_name  # Path for downloaded file.

        with open(filepath, 'wb') as f:
            f.write(file_bytes.content)

        # Check that downloaded file's hash matches the expected
        downloaded_hash = self.get_file_hash(filepath)
        if self.uploaded_files.get(downloaded_hash)[0] == file_name:
            print(file_name + " downloaded successfully.")
        else:
            print("WARNING: Downloaded file \"" + file_name + "\"'s hash does not match saved info. It might have "
                                                              "been tampered with.")

    # Checks status on previously uploaded files - prints results to console
    def check_files(self):
        for i in range(len(self.uploaded_files)):
            keys = list(self.uploaded_files.keys())
            key = keys[i]

            i = 1
            while i < len(self.uploaded_files[key]):
                # Deconstruct download URL
                download_url = self.uploaded_files[key][i]
                string_list = download_url.split('/')

                # Build info URL:
                info_url = string_list[0] + "//api." + string_list[2] + "/v2/file/" + string_list[3] + "/info"
                r = requests.get(url=info_url).json()
                if r["status"]:
                    print("The " + self.uploaded_files[key][0] + " download on " + string_list[2] + " is still valid.")
                else:
                    print("The " + self.uploaded_files[key][0] + " link: " + download_url + " is broken.")
                i += 1
                # TODO: Automatically ask user to re-upload files from broken links
