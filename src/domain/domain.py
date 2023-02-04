from src.data.file_handler import file_handler


class domain:
	def __init__(self):
		self.fh = file_handler()  # Automatically loads info about previously uploaded files.

	def upload_file(self, filepath, server):
		encrypted_file_path = filepath  # Edit encrypted_file_path to actually point to an encrypted file.
		return self.fh.upload_file(encrypted_file_path, server)

	def download_file(self, file_hash):
		return self.fh.download_file(file_hash)

	def check_files(self):
		return self.fh.check_files()
