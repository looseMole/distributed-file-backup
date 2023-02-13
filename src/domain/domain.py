import os
from src.data.file_handler import file_handler
from src.domain.encryption_handler import encryption_handler


class domain:
	""" This class combines the domain layer and data layer """

	def __init__(self):
		"""Initialises an instance of the domain class.

		"""
		self.fh = file_handler()  # Automatically loads info about previously uploaded files.
		self.eh = encryption_handler()

	def upload_file(self, filepath, encryption_method, server):
		encrypted_file_path, encryption_key = self.eh.encrypt(filepath, encryption_method)
		if not encrypted_file_path and not encryption_key: # Checks if the encryption was successful
			return False

		file_hash = self.fh.get_file_hash(filepath)
		if not self.fh.upload_file(encrypted_file_path, server, file_hash, encryption_key, encryption_method):
			return False

		return os.remove(encrypted_file_path)

	def download_file(self, file_hash):
		download_feedback = self.fh.download_file(file_hash)
		if not download_feedback[0]: # Checks if it was possible to download the file
			return False

		decrypt_key = self.fh.uploaded_files[download_feedback[3]][2]
		if not self.eh.decrypt(download_feedback[1], "AES", decrypt_key): # TODO: Make this read from the CSV file, depending on the hash of the file.
			return False

		decrypted_file_location = os.path.join(os.path.join(".".join(download_feedback[1].split(os.path.sep)[-1].split(".")[0:-1])))
		if not self.fh.compare_hash(decrypted_file_location, download_feedback[3]):
			print("Warning: The downloaded file's hash does not match the stored. The file might have been tampered with.")
			return False

		return True


	def check_files(self):
		return self.fh.check_files()
