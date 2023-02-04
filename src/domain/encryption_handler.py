import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class encryption_handler(object):
	def __init__(self):
		pass

	def check_files(self):
		pass


class encryptAES(encryption_handler):

	def __init__(self, file_path, original_file, encrypted_file):
		super().__init__()
		self.key = None
		self.file_path = file_path

		self.encrypt()
		self.decrypt()

	def encrypt(self):
		self.key = os.urandom(32)
		iv = os.urandom(16)

		cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), default_backend())  # TODO: Use GCM instead of CBC
		padder = padding.PKCS7(128).padder()
		encrypter = cipher.encryptor()

		with open(self.file_path, "rb") as original_file:
			with open(self.file_path + ".edfb", "wb") as encrypted_file:
				encrypted_file.write(iv)

				original_text = b""
				while True:
					# TODO: Add support for handling files in chunks
					_n = original_file.read(-1)
					if not _n:
						break

					original_text += _n

				padded_text = padder.update(original_text)
				padded_text += padder.finalize()
				encrypted_text = encrypter.update(padded_text)
				encrypted_file.write(encrypted_text + encrypter.finalize())

	def decrypt(self):
		with open(self.file_path + ".edfb", "rb") as encrypted_file:
			iv = encrypted_file.read(16)
			cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), default_backend())  # TODO: Use GCM instead of CBC
			unpadder = padding.PKCS7(128).unpadder()
			decryptor = cipher.decryptor()

			with open(self.file_path, "wb") as decrypted_file: # TODO: The name for the decrypted file should not be the same as the original

				encrypted_text = b""
				while True:
					# TODO: Add support for handling files in chunks
					_n = encrypted_file.read(-1)
					if not _n:
						break
					encrypted_text += _n

				decrypted_text = decryptor.update(encrypted_text)
				unpadded_text = unpadder.update(decrypted_text)

				decrypted_file.write(unpadded_text + unpadder.finalize())

