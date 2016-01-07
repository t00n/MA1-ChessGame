
all:
	python3 main.py

bundle:
	pyinstaller --onefile --windowed main.py
	cp dist/main .
	zip -r chess.zip main data shaders
	rm main

clean:
	rm -rf __pycache__/
	rm -rf build/ dist/ main.spec

mrproper: clean
	rm chess.zip
