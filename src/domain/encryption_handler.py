import os
import shutil
from shutil import move
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class encryption_handler:
	def __init__(self):
		pass

	def check_files(self):
		pass

	def encrypt(self, filepath, encryption_method):
		if encryption_method == "AES":
			return encryptAES(filepath).encrypt()

	def decrypt(self, filepath, decryption_method, encryption_key):
		if decryption_method == "AES":
			return encryptAES(filepath).decrypt(encrypted_filepath=filepath, encryption_key=encryption_key)


class encryptAES:
	""" This class is used to encrypt files with the AES encryption algorithm """

	def __init__(self, filepath):
		"""Initializes an instance of the class and takes the filepath as a parameter

		:param filepath: The path to the file that should be worked on
		"""

		super().__init__()
		self.encryption_key = None
		self.filepath = filepath

	def encrypt(self, filepath=None, encryption_key=None):
		"""Encrypts the file parsed as filepath

		:param filepath: The path to the file that should be encrypted. If no filepath is parsed, the filepath from the class instance will be retrieved.
		:param encryption_key: The encryption key for the file. If no key is parsed, a new will be created

		:returns: A list containing the file name and the encryption key
		"""

		# Checks if a filepath has been set. If not, receives the filepath from the class object.
		if filepath is None:
			filepath = self.filepath

		# Checks if an encryption key has been set. If not, creates a new one.
		if encryption_key is None:
			encryption_key = os.urandom(32)
		else:
			encryption_key = self.encryption_key

		iv = os.urandom(16)

		# Creates the objects for encrypting
		cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), default_backend())  # TODO: Use GCM instead of CBC
		padder = padding.PKCS7(128).padder()
		encrypter = cipher.encryptor()

		# Opens the original file
		try:
			with open(filepath, "rb") as original_file:

				if not os.path.exists(os.path.join('.', 'temp')):
					os.makedirs(os.path.join('.', 'temp'))

				filename = filepath.split(os.path.sep)[-1]

				# Opens the file for what should be encrypted
				with open(os.path.join(os.getcwd(), "temp", filename + ".edfb"), "wb") as encrypted_file:
					# Writes the mode type in the file
					encrypted_file.write(iv)

					# Reads the raw data from the file
					padded_text = padder.update(original_file.read(-1))
					padded_text += padder.finalize()
					encrypted_text = encrypter.update(padded_text)
					encrypted_file.write(encrypted_text + encrypter.finalize())

			# Closes the files
			original_file.close()
			encrypted_file.close()
		except FileNotFoundError:
			print("\nERROR: This file doesn't exist!")
			return [False, False]
		except:
			print("\nERROR: An error occurred while accessing the file")
			return [False, False]

		# Returns the encrypted file name and encryption key
		return [encrypted_file.name, encryption_key]

	def decrypt(self, encrypted_filepath=None, encryption_key=None):
		"""Decrypts the file parsed as encrypted_filepath

		:param encrypted_filepath: The path to the file that should be encrypted. If no filepath is parsed, the filepath from the class instance will be retrieved.
		:param encryption_key: The encryption key for the file. If no filepath is parsed, the encryption key from the class instance will be retrieved.

		:returns: Returns true if the file was successfully decrypted
		"""

		# Checks if the filepath for the encrypted file is set. If not, receives the filepath from the class object.
		if encrypted_filepath is None:
			encrypted_filepath = self.filepath

		# Checks if the encryption key is set. If not, receives the encryption key from the class object.
		if encryption_key is None:
			encryption_key = self.encryption_key

		# Opens the encrypted file
		try:
			with open(encrypted_filepath, "rb") as encrypted_file:
				# Retrieves information from the file
				iv = encrypted_file.read(16)

				# Creates the objects for decrypting the file
				cipher = Cipher(algorithms.AES(bytes.fromhex(encryption_key)), modes.CBC(iv), default_backend())  # TODO: Use GCM instead of CBC
				unpadder = padding.PKCS7(128).unpadder()
				decryptor = cipher.decryptor()

				# Opens a new file for the decrypted file
				decrypted_file_location = os.path.join(os.path.join(f"{os.path.sep}".join(encrypted_filepath.split(os.path.sep)[0:-1])), ".".join(encrypted_filepath.split(os.path.sep)[-1].split(".")[0:-1]))

				with open(decrypted_file_location, "wb") as decrypted_file: # TODO: The name for the decrypted file should not be the same as the original
					# Decrypts the data and writes it to the decrypted file
					decrypted_text = decryptor.update(encrypted_file.read(-1))
					unpadded_text = unpadder.update(decrypted_text)
					decrypted_file.write(unpadded_text + unpadder.finalize())

			# Closes both files
			decrypted_file.close()
			encrypted_file.close()
		except FileNotFoundError:
			print("\nERROR: This file dosen't exist")
			return [False, False]

		# Removes the encrypted file, since it doesn't need to be used anymore
		os.remove(encrypted_filepath)
		try:
			move(decrypted_file_location, os.path.join(".")) # TODO: Check if it works
		except shutil.Error:
			print("\nWARNING: The file already exists. It was NOT overridden!")
			return False

		# Returns true, because the file was successfully decrypted
		return True
