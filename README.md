# Metronomnom

A simple metronome application built with Python.

> **Note**: Metronomnom is currently in beta. I'm actively working on it, but all main features are functional.

## Features

- Adjustable BPM (10-400)
- Multiple rhythm modes (normal, eighth notes, triplets, sixteenth notes)
- Customizable time signatures (1/4 to 9/4)
- Command-line interface
- Optional Textual-based UI

## Commands

- Numbers: Set BPM
- `s`: Stop metronome
- `q`: Quit application
- `e`: Toggle eighth notes
- `t`: Toggle triplet mode
- `x`: Toggle sixteenth notes
- `1-9`: Set time signature (e.g., `3` for 3/4 time)

## Installation

```bash
git clone https://github.com/yourusername/metronomnom.git
cd metronomnom
pip install -r requirements.txt
```

## Usage

### Command Line Interface
```bash
python main.py
```

### Textual UI (if installed)
```bash
python interface.py
```

## Requirements

- Python 3.7+
- pygame
- textual (for UI version)
