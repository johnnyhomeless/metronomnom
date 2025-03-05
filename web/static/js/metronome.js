// Metronome state
let bpm = 120;
let isRunning = false;
let currentBeat = 1;
let beatsPerMeasure = 4;
let rhythmMode = 'normal'; // Can be 'normal', 'eighth', 'triplet', 'sixteenth'

// Audio context (for Web Audio API)
let audioContext = null;
let audioBuffers = {}; // Store multiple audio files

// Core functions (you'll implement these)
function initializeAudio() {

    // Initialize Web Audio API context if it doesn't exist yet
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    function loadAudio(fileName) {
        return fetch(fileName)
            .then(response => response.arrayBuffer())
            .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
            .then(decodedAudio => {
                audioBuffers[fileName] = decodedAudio; // Store it in the object
                console.log(`Audio loaded: ${fileName}`);
            })
            .catch(error => console.error(`Error loading ${fileName}:`, error));
    }
    
    loadAudio("static/sounds/4c.wav");
    loadAudio("static/sounds/4d.wav");
    loadAudio("static/sounds/tripl.wav");
}

function startMetronome() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    // Start the metronome logic...
}

function stopMetronome() {
    // Stop the metronome
}

function updateBPM(newBPM) {
    // Update the tempo
}

function setRhythmMode(mode) {
    // Change subdivision mode
}

function setTimeSignature(beats) {
    // Change time signature
}

// Event listeners (connect when DOM is loaded)
document.addEventListener('DOMContentLoaded', function() {
    // Connect buttons and controls to functions
    
    // Example:
    document.getElementById('start-stop').addEventListener('click', function() {
        if (isRunning) {
            stopMetronome();
        } else {
            startMetronome();
        }
    });
    
    // Initialize other UI connections here
});