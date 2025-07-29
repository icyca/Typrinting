const prompts = {
    easy: [
        "The quick brown fox jumps over the lazy dog.",
        "Pack my box with five dozen liquor jugs.",
        "How vexingly quick daft zebras jump!",
        "Sphinx of black quartz, judge my vow.",
        "Waltz, nymph, for quick jigs vex Bud."
    ],
    medium: [
        "The five boxing wizards jump quickly over the lazy dog while the sphinx of black quartz judges my vow.",
        "Pack my box with five dozen liquor jugs and watch the quick brown fox jump over the lazy dog.",
        "How vexingly quick daft zebras jump while the sphinx of black quartz judges my vow carefully."
    ],
    hard: [
        "The five boxing wizards jump quickly over the lazy dog while the sphinx of black quartz judges my vow with careful consideration of the intricate patterns.",
        "Pack my box with five dozen liquor jugs and watch the quick brown fox jump over the lazy dog as the sphinx of black quartz judges my vow.",
        "How vexingly quick daft zebras jump while the sphinx of black quartz judges my vow with careful consideration of the intricate patterns."
    ]
};

let holdTimes = [];
let flightTimes = [];
let downDownTimes = [];
let keyDownTimestamps = {};
let lastKeyUpTime = null;
let lastKeyDownTime = null;
let timings = [];
let lastTime = null;
let startTime = null;
let promptText = '';
let errors = 0;
let inputHistory = [];
let currentDifficulty = 'easy';
let isGameActive = false;
let timerInterval;
let currentCharIndex = 0;
let totalChars = 0;

document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    document.getElementById('startBtn').onclick = () => {
        const username = document.getElementById('username').value.trim();
        if (!username) {
            showNotification('Please enter your name.', 'error');
            return;
        }
        document.getElementById('setup').style.display = 'none';
        document.getElementById('game').style.display = 'block';
        startGame();
    };
    document.getElementById('difficultySelect').onchange = (e) => {
        currentDifficulty = e.target.value;
    };
    function startGame() {
        const difficultyPrompts = prompts[currentDifficulty];
        promptText = difficultyPrompts[Math.floor(Math.random() * difficultyPrompts.length)];
        document.getElementById('prompt').innerHTML = formatPrompt(promptText);
        const input = document.getElementById('input');
        input.value = '';
        timings = [];
        inputHistory = [];
        errors = 0;
        lastTime = null;
        startTime = performance.now();
        currentCharIndex = 0;
        totalChars = promptText.length;
        isGameActive = true;
        document.getElementById('time').textContent = '0.00';
        document.getElementById('wpm').textContent = '0';
        document.getElementById('accuracy').textContent = '100%';
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('progressText').textContent = '0%';
        input.focus();
        // Feature arrays
        holdTimes = [];
        flightTimes = [];
        downDownTimes = [];
        keyDownTimestamps = {};
        lastKeyUpTime = null;
        lastKeyDownTime = null;
        // Start timer
        timerInterval = setInterval(updateTimer, 50);
    }
    function formatPrompt(text) {
        return text.split('').map((char, index) => 
            `<span id="char-${index}" class="char">${char}</span>`
        ).join('');
    }
    function updateTimer() {
        if (startTime && isGameActive) {
            const now = performance.now();
            const elapsed = (now - startTime) / 1000;
            document.getElementById('time').textContent = elapsed.toFixed(2);
            // Update WPM
            const wpm = calculateWPM(elapsed);
            document.getElementById('wpm').textContent = Math.round(wpm);
            // Update accuracy
            const accuracy = calculateAccuracy();
            document.getElementById('accuracy').textContent = accuracy + '%';
        }
    }
    function calculateWPM(elapsed) {
        const words = promptText.split(' ').length;
        const minutes = elapsed / 60;
        return words / minutes;
    }
    function calculateAccuracy() {
        if (currentCharIndex === 0) return 100;
        const errorRate = (errors / currentCharIndex) * 100;
        return Math.max(0, Math.round(100 - errorRate));
    }
    document.getElementById('input').onkeydown = (e) => {
        if (!isGameActive) return;
        const now = performance.now();
        keyDownTimestamps[e.code] = now;
        if (lastKeyDownTime !== null) {
            downDownTimes.push(now - lastKeyDownTime);
        }
        lastKeyDownTime = now;
        timings.push({
            key: e.key,
            code: e.code,
            type: 'down',
            time: now - startTime
        });
    };
    document.getElementById('input').onkeyup = (e) => {
        if (!isGameActive) return;
        const now = performance.now();
        const downTime = keyDownTimestamps[e.code];
        if (downTime !== undefined) {
            holdTimes.push(now - downTime);
            if (lastKeyUpTime !== null && downTime !== undefined) {
                flightTimes.push(downTime - lastKeyUpTime);
            }
            lastKeyUpTime = now;
        }
        timings.push({
            key: e.key,
            code: e.code,
            type: 'up',
            time: now - startTime
        });
    };
    document.getElementById('input').oninput = (e) => {
        if (!isGameActive) return;
        const val = e.target.value;
        inputHistory.push({
            value: val,
            time: performance.now() - startTime
        });
        // Update character highlighting
        updateCharacterHighlighting(val);
        // Update progress
        const progress = (val.length / totalChars) * 100;
        document.getElementById('progressBar').style.width = progress + '%';
        document.getElementById('progressText').textContent = Math.round(progress) + '%';
        // Check for completion
        if (val === promptText) {
            finishGame();
        }
    };
    function updateCharacterHighlighting(input) {
        // Reset all characters
        for (let i = 0; i < totalChars; i++) {
            const charElement = document.getElementById(`char-${i}`);
            charElement.className = 'char';
        }
        // Highlight current and completed characters
        for (let i = 0; i < input.length && i < totalChars; i++) {
            const charElement = document.getElementById(`char-${i}`);
            if (input[i] === promptText[i]) {
                charElement.className = 'char correct';
            } else {
                charElement.className = 'char incorrect';
                if (i === input.length - 1) errors++;
            }
        }
        // Highlight next character
        if (input.length < totalChars) {
            const nextChar = document.getElementById(`char-${input.length}`);
            nextChar.className = 'char current';
        }
        currentCharIndex = input.length;
    }
    function finishGame() {
        isGameActive = false;
        clearInterval(timerInterval);
        const totalTime = (performance.now() - startTime) / 1000;
        const finalWpm = calculateWPM(totalTime);
        const finalAccuracy = calculateAccuracy();
        // Show results
        document.getElementById('game').style.display = 'none';
        document.getElementById('result').style.display = 'block';
        const resultHTML = `
            <div class="result-card">
                <h2>🎉 Great Job!</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <span class="stat-value">${totalTime.toFixed(2)}s</span>
                        <span class="stat-label">Time</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${Math.round(finalWpm)}</span>
                        <span class="stat-label">WPM</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${finalAccuracy}%</span>
                        <span class="stat-label">Accuracy</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${errors}</span>
                        <span class="stat-label">Errors</span>
                    </div>
                </div>
                <div class="performance-indicator">
                    ${getPerformanceMessage(finalWpm, finalAccuracy)}
                </div>
            </div>
        `;
        document.getElementById('result').innerHTML = resultHTML;
        // Send data
        sendData({
            username: document.getElementById('username').value.trim(),
            text: promptText,
            hold_times: holdTimes,
            flight_times: flightTimes,
            down_down_times: downDownTimes,
            timings,
            inputHistory,
            errors,
            totalTime,
            wpm: finalWpm,
            accuracy: finalAccuracy,
            difficulty: currentDifficulty,
            timestamp: new Date().toISOString()
        });
    }
    function getPerformanceMessage(wpm, accuracy) {
        if (wpm >= 80 && accuracy >= 95) return "🏆 Elite Typist!";
        if (wpm >= 60 && accuracy >= 90) return "🚀 Excellent!";
        if (wpm >= 40 && accuracy >= 85) return "👍 Good Job!";
        if (wpm >= 30 && accuracy >= 80) return "📈 Keep Practicing!";
        return "💪 You'll Get Better!";
    }
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    function updateStats() {
        // Placeholder for future stats
    }
    function sendData(data) {
        fetch('/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(res => {
            showNotification('Data saved successfully!', 'success');
        })
        .catch(err => {
            showNotification('Error saving data.', 'error');
        });
    }
    // Add restart functionality
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !isGameActive && document.getElementById('result').style.display === 'block') {
            document.getElementById('result').style.display = 'none';
            document.getElementById('setup').style.display = 'block';
        }
    });
}); 