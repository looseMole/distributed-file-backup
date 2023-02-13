from src.domain.domain import domain
import os


class CLI:
    def __init__(self):
        pass

    def main(self):
        domain_object = domain()

        while True:
            self.print_help()
            try:
                msg = int(input(">>>"))
            except ValueError:
                print("\nThis input is not allowed!")
                continue

            if msg == 1:  # Upload
                print("\nPlease type the full path to the file you want to upload:")
                msg_file_path = input(">>>")

                print("\nPlease choose the server you with to upload to:")
                server_list = []
                for key in domain_object.fh.server_switcher.keys():
                    server_list.append(key)

                print(str(server_list), sep=", ")
                msg_server_choice = input(">>>")

                if domain_object.upload_file(msg_file_path, "AES", msg_server_choice): # TODO: Let the use choose between different encryption algorithms
                    print("\nFile successfully uploaded!\nThe file can be downloaded again through the option: [2] Download file")

            elif msg == 2:  # Download
                print("\nPlease choose a file from the table below:")
                domain_object.fh.print_file_information()
                print("")
                msg_download_file = input(">>>")
                if domain_object.download_file(msg_download_file):
                    print("\nFile successfully downloaded!")

            elif msg == 3:  # Check files
                response = domain_object.check_files()
                if len(response) == 1 and not response[0]:
                    print("No previously uploaded files found.")

                elif not response[0]:
                    broken_links = response[1]
                    uploaded_files = domain_object.fh.uploaded_files

                    for i in range(0, len(broken_links), 3):
                        key = broken_links[i]
                        broken_url = broken_links[i + 1]
                        enc_method = broken_links[i + 2]
                        amount_of_valid_links = 0
                        file_name = uploaded_files[key][0]

                        string_list = broken_url.split('/')
                        broken_down_name = string_list[2]

                        #  Finds first valid alt link for file:
                        for j in range(1, len(uploaded_files[key]), 3):
                            if not uploaded_files[key][j] in broken_links:
                                amount_of_valid_links += 1
                                good_url = uploaded_files[key][j]

                                string_list = good_url.split('/')
                                good_down_name = string_list[2]
                                break

                        print("\n\"" + uploaded_files[key][0] + "\"" + " link: " + broken_url + " is broken.")

                        if amount_of_valid_links > 0:
                            print(
                                "Would you like to download \"" + file_name + "\" from " + good_down_name +
                                ", and re-upload it to " + broken_down_name + "?\t(Y/N)")
                            valid_responses = ['y', 'Y', 'n', 'N']
                            usr_resp = input(">>>")

                            # Make sure to get a valid response.
                            while not usr_resp in valid_responses:
                                print("Invalid input.\n")
                                print(
                                    "Would you like to download \"" + file_name + "\" from " + good_down_name +
                                    ", and re-upload it to " + broken_down_name + "?\t(Y/N)")
                                usr_resp = input(">>>")

                            if usr_resp in valid_responses[0:1]:
                                # Download file from valid link:  TODO: Check if the file is already downloaded, and if so, don't download it again.
                                domain_object.fh.remove_download_link(key, broken_url)
                                if domain_object.download_file(key): # NB: Only tries to download once. Should this be changed?
                                    print("File downloaded.")

                                string_list = good_down_name.split('.')
                                server = string_list[0] #  Get upload_file server name.
                                filepath = os.path.join('.', file_name.replace(".edfb", "")) # Get path of downloaded file TODO: Change upload folder according to download folder.
                                if domain_object.upload_file(filepath, enc_method, server):  # Re-upload file. Assume a failed download means file already exists.
                                    print("\nFile successfully uploaded!\nThe file can be downloaded again through the option: [2] Download file")
                                else:
                                    print("Error in uploading file.")


                            elif usr_resp in valid_responses[2:]:
                                print("No download links deleted.")

                        else:  # No valid download links for this file.
                            print("\nNo valid alternative downloads found.")
                            print("Would you like to remove \"" + file_name + "\" from list of uploaded files?\t(Y/N)")

                            valid_responses = ['y', 'Y', 'n', 'N']
                            usr_resp = input(">>>")

                            # Make sure to get a valid response.
                            while not usr_resp in valid_responses:
                                print("Invalid input.\n")
                                print("Would you like to remove \"" + file_name + "\" from list of uploaded files?\t(Y/N)")
                                usr_resp = input(">>>")

                            if usr_resp in valid_responses[0:1]:
                                domain_object.fh.remove_download_link(key, broken_url)
                else:
                    pass  # All file download links were valid.


            elif msg == 4:
                print("Quitting")
                break

    def print_help(self):
        print("\nThis application allows you to use the following commands:")
        print(" [1] Upload file")
        print(" [2] Download file")
        print(" [3] Check files")
        print(" [4] Exit")
        print("\nPlease enter the corresponding number for the command you want to use:")


if __name__ == "__main__":
    cli_object = CLI()
    cli_object.main()
