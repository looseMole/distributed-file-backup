from src.domain.domain import domain


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

                else:
                    print("An error occurred while uploading the file.")

            elif msg == 2:  # Download
                print("\nPlease choose a file from the table below:")
                domain_object.fh.print_file_information()
                print("")
                msg_download_file = input(">>>")
                if domain_object.download_file(msg_download_file):
                    print("File successfully downloaded!")

            elif msg == 3:  # Check files
                if not domain_object.check_files():
                    print("No previously uploaded files found.")

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
