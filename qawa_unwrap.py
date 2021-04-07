import os

def unwrap(SOURCE_DIR):
	files = []
	for (dirpath, dirnames, filenames) in os.walk(SOURCE_DIR):
		files += [os.path.join(dirpath, file).replace(SOURCE_DIR,'') for file in filenames]
	files = set([file for file in files if '.qawa_copy' in file])
	print(f"Restoring: {files}")
	for file_copy in files:
		file_original = file_copy.replace('.qawa_copy', '')
		os.remove(f"{SOURCE_DIR}/{file_original}")
		os.rename(f"{SOURCE_DIR}/{file_copy}", f"{SOURCE_DIR}/{file_original}")