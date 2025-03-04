# Metronomnom

A simple Python metronome with both command-line and text-based UI options.

## Features

- BPM range: 10-400 
- Rhythm patterns: normal, eighth notes, triplets, sixteenth notes
- Customizable time signatures (1-9 beats per measure)
- First beat accent
- Tap tempo functionality (UI version)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/metronomnom.git
cd metronomnom

# Install dependencies
pip install pygame
pip install textual  # Only needed for UI version
```

## Usage

### Command Line Interface

```bash
# Run the CLI version
python src/main.py
```

### Text-based UI (Textual)

```bash
# Run the UI version
python src/interface.py
```

## Commands

- Enter a number (10-400) to set BPM
- `q` - Quit
- `s` - Stop metronome
- `e` - Toggle eighth note subdivision
- `t` - Toggle triplet subdivision
- `x` - Toggle sixteenth note subdivision
- `1-9` - Set time signature (beats per measure)

## Project Structure

- `src/` - Source code
  - `main.py` - Command line interface
  - `metronome.py` - Core metronome functionality
  - `constants.py` - Configuration and language strings
  - `interface.py` - Text-based UI
- `src/sounds/` - Audio files

## License

MIT

## Future Plans

- Additional sound options
- Web interface
- Multiple language support
