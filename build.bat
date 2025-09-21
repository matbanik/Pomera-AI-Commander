@echo off
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install pyinstaller reportlab python-docx typing-extensions requests Metaphone lemminflect pyaudio numpy anthropic openai cohere huggingface_hub groq
echo Building executable...
pyinstaller --onedir --windowed --name promera_ai promera_ai.py
echo Build complete.
Executable is in the 'dist' folder.
pause