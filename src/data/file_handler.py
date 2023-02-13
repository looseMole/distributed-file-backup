import os
import csv
import hashlib
import requests
from tqdm import tqdm


class file_handler:
    uploaded_files = {}
    csv_file_name = "distributed_file_backup_info.csv"
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

    # Uses os.path to find relative paths to documents, to support different OS' filesystems.
    doc_path = os.path.join('~', 'Documents')
    csv_file_path = os.path.expanduser(doc_path)
    csv_file_path = os.path.join(csv_file_path, csv_file_name)

    def __init__(self):

        self.are_servers_up()
        self.load_links()

    # Loads information about previously uploaded files, from CSV-file.
    def load_links(self):
        try:
            with open(self.csv_file_path, 'r') as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if len(line) > 0:
                        line_parts = line[0].split('|')
                        self.uploaded_files[line_parts[0]] = []
                        for i in range(len(line_parts)):
                            if (i + 1) >= len(line_parts) : break
                            self.uploaded_files[line_parts[0]].append(line_parts[i+1])
                f.close()

        except FileNotFoundError:
            pass

    # Checks up-status of the servers specified in server_switcher. Prints result
    def are_servers_up(self):
        print("Checking the status for all servers. This might take a few seconds...")

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
                print("All servers are running!")

    # Saves information from uploaded_files to a CSV-file.
    def save_links(self):
        with open(self.csv_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            keys = list(self.uploaded_files.keys())
            for i in range(len(self.uploaded_files)):
                key = keys[i]
                file_string = key
                for j in range(len(self.uploaded_files[key])):
                    file_string += "|" + self.uploaded_files[key][j]

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

    def get_encryption_key(self, filehash):
        for _filehash in self.uploaded_files:
            if _filehash == filehash:
                return self.uploaded_files.get(_filehash)[2]
        return None

    # Uploads file to specified server, then calls save_links().
    def upload_file(self, filepath, server, file_hash, encryption_key, encryption_method):
        url = self.server_switcher.get(server, "")
        if url == "":
            print("\nERROR: Invalid server!")
            return False

        # TODO: Create exception handling for invalid filepath.
        with open(filepath, "rb") as a_file:
            filename = os.path.basename(filepath)
            _files = {"file": (filename, a_file)}
            r = requests.post(url=url, files=_files).json()
            # print(r)  # Print response from server, received as a JSON.

        if r["status"]:
            download_url = r["data"]["file"]["url"]["full"]
            # If a file with this SHA1-hash has already been uploaded, append the download to that file.
            if file_hash in self.uploaded_files:
                self.uploaded_files[file_hash].append(download_url)
                self.uploaded_files[file_hash].append(encryption_key.hex())
                self.uploaded_files[file_hash].append(encryption_method)
            else:
                self.uploaded_files[file_hash] = [filename, download_url, encryption_key.hex(), encryption_method]
            self.save_links()
            return True
        else:
            return False

    def download_file(self, file_hash):
        try:
            # Deconstruct download URL
            download_url = self.uploaded_files[file_hash][1]  # Note: Currently only tries the first download link.
            string_list = download_url.split('/')
        except KeyError:
            n = 0
            represented_hash = ""
            for i in self.uploaded_files.keys():
                if str(i[0:len(file_hash)]) == str(file_hash):
                    n += 1
                    represented_hash = i
            if n == 1:
                file_hash = represented_hash
                download_url = self.uploaded_files[file_hash][1]  # Note: Currently only tries the first download link.
                string_list = download_url.split('/')
            else:
                print("\nERROR: Not a valid file hash!")
                return [False, None, None, None]


        # Build info URL:
        info_url = string_list[0] + "//api." + string_list[2] + "/v2/file/" + string_list[3] + "/info"
        r = requests.get(url=info_url).json()

        if r["status"]:
            # Fixes issue with server replacing periods (.) with underscores (_)
            underscore_name = r['data']['file']['metadata']['name']
            underscore_index = underscore_name.rindex('_')
            file_name = list(r['data']['file']['metadata']['name'])
            file_name[underscore_index] = "."
            file_name = ''.join(file_name)
            file_size = r['data']['file']['metadata']['size']['bytes']

            print("\nDownloading file, please wait...")

        else:
            print("The link: " + download_url + " is broken.")
            return [False, None, None, None]

        if not os.path.exists(os.path.join('.', 'temp')):
            os.makedirs(os.path.join('.', 'temp'))

        # Get direct download link.
        r = requests.get(download_url)
        direct_url_start = r.text.find("https://cdn")
        direct_url_end = r.text.find("\"", direct_url_start)
        direct_url = r.text[direct_url_start:direct_url_end]

        filepath = os.path.join('.', 'temp', file_name)  # Path for temp folder.

        # Download is streamed, in chunks of 64KB as opposed to loaded entirely into memory.
        with requests.get(direct_url, stream=True) as r:
            r.raise_for_status()  # Will raise error, if response is bad.
            with open(filepath, 'wb') as f:
                downloaded_bytes = 0
                c_size = 65536  # Size of chunk to load into memory.
                progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
                for chunk in r.iter_content(chunk_size=c_size):
                    f.write(chunk)  # Write to file
                    downloaded_bytes += c_size

                    progress_bar.update(c_size)

        # Check that downloaded file's hash matches the expected
        downloaded_hash = self.get_file_hash(filepath)
        encryption_key = self.get_encryption_key(downloaded_hash)


        return [True, filepath, encryption_key, file_hash]

    def compare_hash(self, filepath, file_hash):
        new_hash = self.get_file_hash(filepath)
        if new_hash == file_hash:
            return True
        else:
            return False

    def print_file_information(self):
        for key in self.uploaded_files.keys():
            print(key + "\t\t" + self.uploaded_files[key][0])

    # Checks status on previously uploaded files - prints results to console
    def check_files(self):
        if len(self.uploaded_files) == 0:
            return False

        for i in range(len(self.uploaded_files)):
            keys = list(self.uploaded_files.keys())
            key = keys[i]

            for j in range(1, len(self.uploaded_files[key]), 3):
                # Deconstruct download URL
                download_url = self.uploaded_files[key][j]
                string_list = download_url.split('/')

                # Build info URL:
                info_url = string_list[0] + "//api." + string_list[2] + "/v2/file/" + string_list[3] + "/info"
                r = requests.get(url=info_url).json()
                if r["status"]:
                    print("VALID FILE:\t\t\t" + self.uploaded_files[key][0] + " from " + string_list[2])
                else:
                    print("INVALID FILE:\t\t" + self.uploaded_files[key][0] + " from " + download_url)
                i += 1
                # TODO: Automatically ask user to re-upload files from broken links
        return True
