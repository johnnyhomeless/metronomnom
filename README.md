# Metronomnom 🍕🎵  

A simple command-line metronome written in Python.

## Features

- Simple command-line interface
- BPM range from 10 to 400
- Start/stop functionality
- Real-time BPM adjustment
- Clear audio beats
- Error handling for invalid inputs

## Requirements

- Python 3.x
- pygame

## Installation

1. Clone this repository:
```bash
git clone https://github.com/johnnyhomeless/metronomnom.git
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install pygame
```

## Usage

1. Start the program:
```bash
python src/main.py
```

2. Commands:
- Enter a number between 10-400 to set BPM
- `s` to stop the metronome
- `q` to quit the program

## Example Usage

```
Enter BPM (or 'q' to quit, 's' to stop): 120
Metronome started. Press 's' to stop.
Enter BPM (or 'q' to quit, 's' to stop): 140
Tempo changed to 140 BPM
Enter BPM (or 'q' to quit, 's' to stop): s
Metronome stopped.
Enter BPM (or 'q' to quit, 's' to stop): q
Goodbye!
```

## Project Structure

```
src/
├── main.py         # Main program logic
├── metronome.py    # Metronome class implementation
├── constants.py    # Configuration and messages
└── sounds/         # Audio files
    └── 4d.wav      # Metronome sound
```

## Testing

Run the test suite:
```bash
python -m unittest src/test_metronome.py
```

## Contributing

Feel free to submit issues and pull requests.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
