import os
if os.name == 'nt':
	from src.presentation.CLI import CLI
else:
	from presentation.CLI import CLI

if __name__ == "__main__":
	cli = CLI()
	cli.main()
