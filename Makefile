.PHONY: run clean freeze package

run:
	python video.py

freeze:
	pip freeze > requirements.txt

package:
	pyinstaller --onefile --windowed --name video_tool video.py

clean:
	rm -rf build dist __pycache__ *.spec
