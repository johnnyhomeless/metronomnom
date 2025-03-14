const LOOKAHEAD_MS = 25.0;
const SCHEDULE_AHEAD_TIME = 0.1;
const MIN_BPM = 10;
const MAX_BPM = 400;
const MAX_NOTIFICATIONS = 2;

const startStopButton = document.getElementById('start-stop');
const beatDisplay = document.getElementById('beat-display');
const bpmInput = document.getElementById('bpm-input');
const timeSignatureSelect = document.getElementById('time-signature');
const modeButtons = document.querySelectorAll('[id^="mode-"]');
const bpmSlider = document.getElementById('myRange');

const tempoMarkings = [
    { min: 10, max: 24, name: "Larghissimo" },
    { min: 25, max: 39, name: "Grave" },
    { min: 40, max: 44, name: "Largo" },
    { min: 45, max: 59, name: "Lento" },
    { min: 60, max: 65, name: "Larghetto" },
    { min: 66, max: 71, name: "Adagio" },
    { min: 72, max: 75, name: "Adagietto" },
    { min: 76, max: 79, name: "Andante" },
    { min: 80, max: 82, name: "Andantino" },
    { min: 83, max: 85, name: "Marcia moderato" },
    { min: 86, max: 91, name: "Andante moderato" },
    { min: 92, max: 107, name: "Moderato" },
    { min: 108, max: 111, name: "Allegretto" },
    { min: 112, max: 119, name: "Allegro moderato" },
    { min: 120, max: 167, name: "Allegro" },
    { min: 168, max: 171, name: "Vivace" },
    { min: 172, max: 175, name: "Vivacissimo" },
    { min: 176, max: 199, name: "Allegrissimo (Allegro vivace)" },
    { min: 200, max: 299, name: "Presto" },
    { min: 300, max: 400, name: "Prestissimo" }
];

let bpm = 120;
let nextNoteTime = 0.0;
let notesInQueue = [];
let isRunning = false;
let currentBeat = 1;
let beatsPerMeasure = 4;
let rhythmMode = 'normal';
let timerID = null;
let audioLoaded = false;
let lastDisplayedBeat = 0;
let tapTimes = [];
let maxTapAge = 5000;
let minTapsRequired = 2;
let activeNotifications = 0;
let audioContext = null;
let audioBuffers = {};

function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification-container');
    
    if (activeNotifications >= MAX_NOTIFICATIONS) {
        if (container.firstChild) {
            container.firstChild.classList.remove('show');
            
            setTimeout(() => {
                if (container.firstChild) {
                    container.removeChild(container.firstChild);
                    activeNotifications--;
                    
                    addNotification();
                }
            }, 300);
            return;
        }
    } else {
        addNotification();
    }
    
    function addNotification() {
        activeNotifications++;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
    
        container.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 1);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                container.removeChild(notification);
                activeNotifications--;
            }, 300);
        }, duration);
    }
}

function initializeAudio() {
    if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
    if (audioLoaded) return Promise.resolve();
    return Promise.all([
        loadAudio("static/sounds/4c.wav"),
        loadAudio("static/sounds/4d.wav"),
        loadAudio("static/sounds/tripl.wav")
    ]).then(() => audioLoaded = true);
}

function loadAudio(fileName) {
    return fetch(fileName)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
        .then(decodedAudio => audioBuffers[fileName] = decodedAudio);
}

function updateBeatDisplay(beatNumber) {
    if (beatDisplay && beatNumber !== lastDisplayedBeat) {
        beatDisplay.textContent = beatNumber;
        lastDisplayedBeat = beatNumber;
    }
}

function updateBPM(newBPM) {
    bpm = newBPM;
    document.getElementById('current-bpm').textContent = bpm;
    bpmInput.value = bpm;
    bpmSlider.value = bpm;
    
    updateTempoMarking(bpm);
}

function updateTempoMarking(bpm) {
    const tempoElement = document.getElementById('tempo-marking');
    
    if (bpm >= 400) {
        tempoElement.textContent = "Prestissimo 🚀";
        return;
    }
    
    for (const tempo of tempoMarkings) {
        if (bpm >= tempo.min && bpm <= tempo.max) {
            tempoElement.textContent = tempo.name;
            return;
        }
    }
    
    tempoElement.textContent = "";
}

function updateUI(running) {
    startStopButton.textContent = running ? 'Stop' : 'Start';
    startStopButton.classList.toggle('stopping', running);
    
    if (running) {
        showNotification('Metronome started', 'success');
    } else {
        showNotification('Metronome stopped', 'error');
    }
}

function getSubdivisionCount() {
    switch (rhythmMode) {
        case 'eighth': return 2;
        case 'triplet': return 3;
        case 'sixteenth': return 4;
        default: return 1;
    }
}

function nextNote() {
    nextNoteTime += 60.0 / bpm;
    currentBeat = currentBeat % beatsPerMeasure + 1;
}

function scheduleNote(beatNumber, time) {
    if (!audioLoaded || !audioBuffers["static/sounds/4c.wav"]) return;
    
    notesInQueue.push({
        beat: beatNumber,
        time: time
    });
    
    const subdivisions = getSubdivisionCount();
    
    if (subdivisions === 1) {
        const source = audioContext.createBufferSource();
        source.buffer = (beatNumber === 1) ? 
            audioBuffers["static/sounds/4c.wav"] : 
            audioBuffers["static/sounds/4d.wav"];
        source.connect(audioContext.destination);
        source.start(time);
        return;
    }
    
    const beatDuration = 60.0 / bpm;
    const subdivisionDuration = beatDuration / subdivisions;
    
    for (let i = 0; i < subdivisions; i++) {
        const subdivisionTime = time + (i * subdivisionDuration);
        const source = audioContext.createBufferSource();
        
        if (i === 0) {
            source.buffer = (beatNumber === 1) ? 
                audioBuffers["static/sounds/4c.wav"] : 
                audioBuffers["static/sounds/4d.wav"];
        } else {
            source.buffer = audioBuffers["static/sounds/tripl.wav"];
        }
        
        source.connect(audioContext.destination);
        source.start(subdivisionTime);
    }
}

function scheduler() {
    while (nextNoteTime < audioContext.currentTime + SCHEDULE_AHEAD_TIME) {
        scheduleNote(currentBeat, nextNoteTime);
        nextNote();
    }
    
    while (notesInQueue.length && notesInQueue[0].time < audioContext.currentTime) {
        updateBeatDisplay(notesInQueue[0].beat);
        notesInQueue.shift();
    }
    
    if (isRunning) {
        timerID = setTimeout(scheduler, LOOKAHEAD_MS);
    }
}

function startMetronomeEngine() {
    isRunning = true;
    currentBeat = 1;
    notesInQueue = [];
    nextNoteTime = audioContext.currentTime;
    scheduler();
    updateUI(true);
    updateBeatDisplay(currentBeat);
}

function startMetronome() {
    if (audioContext.state === 'suspended') audioContext.resume();
    if (isRunning) return;
    if (!audioLoaded) {
        showNotification('Loading sounds...', 'info');
        initializeAudio()
            .then(startMetronomeEngine)
            .catch(() => showNotification('Error loading sounds', 'error'));
    } else {
        startMetronomeEngine();
    }
}

function stopMetronome() {
    if (!isRunning) return;
    isRunning = false;
    if (timerID) clearTimeout(timerID);
    notesInQueue = [];
    updateUI(false);
}

function setTimeSignature(beats) {
    beats = parseInt(beats);
    if (!isNaN(beats) && beats >= 1 && beats <= 12) {
        beatsPerMeasure = beats;
        if (currentBeat > beatsPerMeasure) {
            currentBeat = 1;
            updateBeatDisplay(currentBeat);
        }
        showNotification(`Time signature changed to ${beats}/4`, 'info');
    }
}

function calculateTapTempo() {
    const intervals = [];
    for (let i = 1; i < tapTimes.length; i++) {
        intervals.push(tapTimes[i] - tapTimes[i-1]);
    }
    
    const averageInterval = intervals.reduce((sum, interval) => sum + interval, 0) / intervals.length;
    let calculatedBpm = Math.round(60000 / averageInterval);
    calculatedBpm = Math.max(MIN_BPM, Math.min(calculatedBpm, MAX_BPM));
    
    return calculatedBpm;
}

function handleTap() {
    const currentTime = performance.now();
    tapTimes = tapTimes.filter(time => currentTime - time < maxTapAge);
    tapTimes.push(currentTime);
    
    const tapButton = document.getElementById('tap-tempo');
    tapButton.classList.add('tapped');
    
    setTimeout(() => {
        tapButton.classList.remove('tapped');
    }, 100);
    
    if (tapTimes.length >= minTapsRequired) {
        const calculatedBpm = calculateTapTempo();
        bpmInput.value = calculatedBpm;
        updateBPM(calculatedBpm);
    } else {
        showNotification('Tap again to set tempo...', 'info');
    }
}

function setRhythmMode(mode) {
    rhythmMode = mode;
    showNotification(`Switched to ${mode} mode`, 'info');
}

document.addEventListener('DOMContentLoaded', () => {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    initializeAudio();
    showNotification('Welcome to Metronomnom!', 'info', 5000);
    
    startStopButton.addEventListener('click', () => isRunning ? stopMetronome() : startMetronome());
    document.getElementById('tap-tempo').addEventListener('click', handleTap);
    
    updateTempoMarking(bpm);
    setRhythmMode('normal');
    document.getElementById('mode-normal').classList.add('active');
    
    bpmSlider.addEventListener('wheel', (event) => {
        event.preventDefault();
        const direction = event.deltaY < 0 ? 1 : -1;
        const increment = 1;
        const newBpm = parseInt(bpmSlider.value) + (direction * increment);
        const clampedBpm = Math.min(MAX_BPM, Math.max(MIN_BPM, newBpm));
        bpmSlider.value = clampedBpm;
        bpmInput.value = clampedBpm;
        updateBPM(clampedBpm);
    });
    
    bpmSlider.addEventListener('input', () => {
        const newBpm = parseInt(bpmSlider.value);
        bpmInput.value = newBpm;
        updateBPM(newBpm);
    });

    bpmInput.addEventListener('change', () => {
        const newBpm = parseInt(bpmInput.value);
        if (!isNaN(newBpm) && newBpm >= MIN_BPM && newBpm <= MAX_BPM) {
            updateBPM(newBpm);
        } else {
            showNotification('Please enter a valid BPM between 10 and 400', 'error');
        }
    });
    
    timeSignatureSelect.addEventListener('change', () => {
        setTimeSignature(timeSignatureSelect.value);
    });
    
    modeButtons.forEach(button => button.addEventListener('click', () => {
        const mode = button.id.replace('mode-', '');
        setRhythmMode(mode);
        modeButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }));
});