# Metronomnom

A versatile metronome application built as a personal learning project. Metronomnom offers both command-line and web interfaces to help musicians keep accurate time.

**Note:** This project was created solely for learning programming concepts and is not intended for commercial use.

## Features

- **Multiple Interfaces:**
  - Command-line text interface
  - Terminal-based UI (using Textual)
  - Web interface (using Flask and Web Audio API)

- **Core Functionality:**
  - BPM range from 10 to 400
  - Multiple rhythm modes (normal, eighth notes, triplets, sixteenth notes)
  - Adjustable time signatures (1/4 through 12/4)
  - First beat accent for easier counting
  - Visual beat indicators

- **Advanced Features:**
  - Tap tempo calculation
  - Musical tempo markings (Allegro, Moderato, Presto, etc.)
  - Notification system in web interface
  - Customizable audio sounds

## Technologies Used

### Backend (Python)
- Python 3.x
- Pygame (for audio processing)
- Textual (for terminal UI)
- Flask (for web server)

### Frontend (Web)
- HTML5 / CSS3 / JavaScript
- Web Audio API (for sound generation)
- Google Fonts (Poppins, Noto Music)

## Project Structure

```
metronomnom/
├── src/                  # Python source code
│   ├── constants.py      # Configuration and text strings
│   ├── main.py           # CLI entry point
│   ├── metronome.py      # Core metronome engine
│   ├── interface.py      # Terminal UI
│   └── sounds/           # Audio files
│       ├── 4c.wav
│       ├── 4d.wav
│       └── tripl.wav
└── web/                  # Web interface
    ├── app.py            # Flask application
    ├── static/
    │   ├── css/
    │   │   └── styles.css
    │   ├── js/
    │   │   └── metronome.js
    │   └── sounds/
    │       └── ...       # Same sound files
    └── templates/
        └── index.html
```

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/metronomnom.git
   cd metronomnom
   ```

2. Install dependencies:
   ```
   pip install pygame flask textual
   ```

## Usage

### Command Line Interface
```
python src/main.py
```

### Terminal UI
```
python src/interface.py
```

### Web Interface
```
cd web
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

## Controls

- **BPM:** Enter a number between 10-400
- **Commands:**
  - 'q' to quit
  - 's' to stop
  - 'e' for eighth notes
  - 't' for triplets
  - 'x' for sixteenth notes
  - '1-9' to set time signature

## Learning Goals

This project was developed to gain experience with:
- Audio programming concepts
- Real-time applications
- User interface design
- Web audio implementation
- Threading in Python
- Event handling
- Cross-platform development

## License

This project is open source and available for personal and educational use.
