// Constants for timing and BPM limits
const LOOKAHEAD_MS = 25.0;          // How often to call scheduler function (ms)
const SCHEDULE_AHEAD_TIME = 0.1;    // How far ahead to schedule audio (seconds)
const MIN_BPM = 10;                 // Minimum tempo
const MAX_BPM = 400;                // Maximum tempo

// Metronome state variables
let bpm = 120;                      // Current tempo
let nextNoteTime = 0.0;             // When the next note is due
let notesInQueue = [];              // Notes that have been scheduled
let isRunning = false;              // Whether metronome is playing
let currentBeat = 1;                // Current position in measure
let beatsPerMeasure = 4;            // Time signature numerator
let rhythmMode = 'normal';          // Current subdivision mode
let timerID = null;                 // Animation frame ID
let audioLoaded = false;            // Sound loading status
let lastDisplayedBeat = 0;          // Track last displayed beat to avoid redundant updates

// Audio system
let audioContext = null;            // Web Audio API context
let audioBuffers = {};              // Loaded sound samples

// DOM element references
const startStopButton = document.getElementById('start-stop');
const statusDisplay = document.getElementById('status-display');
const beatDisplay = document.getElementById('beat-display');
const bpmInput = document.getElementById('bpm-input');
const timeSignatureSelect = document.getElementById('time-signature');
const modeButtons = document.querySelectorAll('[id^="mode-"]');
const bpmSlider = document.getElementById('myRange');

// Initialize audio system and load sound files
function initializeAudio() {
    if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
    if (audioLoaded) return Promise.resolve();
    return Promise.all([
        loadAudio("static/sounds/4c.wav"),      // Downbeat sound
        loadAudio("static/sounds/4d.wav"),      // Regular beat sound
        loadAudio("static/sounds/tripl.wav")    // Subdivision sound
    ]).then(() => audioLoaded = true);
}

// Load and decode a single audio file
function loadAudio(fileName) {
    return fetch(fileName)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
        .then(decodedAudio => audioBuffers[fileName] = decodedAudio);
}

// Start the metronome playback
function startMetronome() {
    if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
    if (audioContext.state === 'suspended') audioContext.resume();
    if (isRunning) return;
    if (!audioLoaded) {
        statusDisplay.textContent = 'Loading sounds...';
        initializeAudio().then(startMetronomeEngine).catch(() => statusDisplay.textContent = 'Error loading sounds');
    } else {
        startMetronomeEngine();
    }
}

// Initialize the engine after sounds are loaded
function startMetronomeEngine() {
    isRunning = true;
    currentBeat = 1;
    notesInQueue = [];
    nextNoteTime = audioContext.currentTime;
    scheduler();
    updateUI(true);
    updateBeatDisplay(currentBeat);  // Initialize beat display
}

// Stop the metronome
function stopMetronome() {
    if (!isRunning) return;
    isRunning = false;
    if (timerID) window.cancelAnimationFrame(timerID);
    notesInQueue = [];
    updateUI(false);
}

// Update UI to reflect metronome state
function updateUI(running) {
    startStopButton.textContent = running ? 'Stop' : 'Start';
    statusDisplay.textContent = running ? 'Metronome started' : 'Metronome stopped';
}

// Update the beat display
function updateBeatDisplay(beatNumber) {
    if (beatDisplay && beatNumber !== lastDisplayedBeat) {
        beatDisplay.textContent = beatNumber;
        lastDisplayedBeat = beatNumber;
    }
}

// Change the tempo
function updateBPM(newBPM) {
    bpm = newBPM;
    document.getElementById('current-bpm').textContent = bpm;
    bpmInput.value = bpm; // Ensure number input is updated
    bpmSlider.value = bpm; // Ensure slider is updated
}

// Update time signature (beats per measure)
function setTimeSignature(beats) {
    beats = parseInt(beats);
    if (!isNaN(beats) && beats >= 1 && beats <= 9) {
        beatsPerMeasure = beats;
        // Reset current beat if it's greater than the new measure length
        if (currentBeat > beatsPerMeasure) {
            currentBeat = 1;
            updateBeatDisplay(currentBeat);
        }
    }
}

// Calculate timing for next beat and advance counter
function nextNote() {
    nextNoteTime += 60.0 / bpm;
    currentBeat = currentBeat % beatsPerMeasure + 1;
}

// Schedule a sound to play at the specified time
function scheduleNote(beatNumber, time) {
    if (!audioBuffers["static/sounds/4c.wav"]) return;
    
    // Add note to queue with beat number and timing info
    notesInQueue.push({
        beat: beatNumber,
        time: time
    });
    
    const source = audioContext.createBufferSource();
    source.buffer = (beatNumber === 1) ? audioBuffers["static/sounds/4c.wav"] : audioBuffers["static/sounds/4d.wav"];
    source.connect(audioContext.destination);
    source.start(time);
}

// Main scheduling function - keeps notes queued ahead of current time
function scheduler() {
    // Schedule notes ahead of current time
    while (nextNoteTime < audioContext.currentTime + SCHEDULE_AHEAD_TIME) {
        scheduleNote(currentBeat, nextNoteTime);
        nextNote();
    }
    
    // Check if any notes in the queue are ready to be displayed
    while (notesInQueue.length && notesInQueue[0].time < audioContext.currentTime) {
        updateBeatDisplay(notesInQueue[0].beat);
        notesInQueue.shift(); // Remove the note we just processed
    }
    
    if (isRunning) timerID = window.requestAnimationFrame(scheduler);
}

// Set up event listeners when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeAudio();
    
    // Start/Stop button
    startStopButton.addEventListener('click', () => isRunning ? stopMetronome() : startMetronome());

    // Add mouse wheel support for the slider
    bpmSlider.addEventListener('wheel', (event) => {
        // Prevent the default scroll behavior
        event.preventDefault();
        
        // Determine direction (negative deltaY means scrolling up)
        const direction = event.deltaY < 0 ? 1 : -1;
        
        // Calculate new BPM value (adjust the increment as needed)
        const increment = 1;
        const newBpm = parseInt(bpmSlider.value) + (direction * increment);
        
        // Ensure BPM stays within valid range
        const clampedBpm = Math.min(MAX_BPM, Math.max(MIN_BPM, newBpm));
        
        // Update the slider, input field and BPM
        bpmSlider.value = clampedBpm;
        bpmInput.value = clampedBpm;
        updateBPM(clampedBpm);
    });
    
    // BPM input
    bpmSlider.addEventListener('input', () => {
        const newBpm = parseInt(bpmSlider.value);
        bpmInput.value = newBpm; // Update the number input as slider moves
        updateBPM(newBpm);
    });

    bpmInput.addEventListener('change', () => {
        const newBpm = parseInt(bpmInput.value);
        if (!isNaN(newBpm) && newBpm >= MIN_BPM && newBpm <= MAX_BPM) updateBPM(newBpm);
    });
    
    // Time signature selector
    timeSignatureSelect.addEventListener('change', () => {
        setTimeSignature(timeSignatureSelect.value);
    });
    
    // Rhythm mode buttons
    modeButtons.forEach(button => button.addEventListener('click', () => {
        rhythmMode = button.id.replace('mode-', '');
        modeButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }));
});