const promptText = "The quick brown fox jumps over the lazy dog.";
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('prompt').textContent = promptText;
    let holdTimes = [];
    let flightTimes = [];
    let downDownTimes = [];
    let keyDownTimestamps = {};
    let lastKeyUpTime = null;
    let lastKeyDownTime = null;
    let isGameActive = true;
    let input = document.getElementById('input');

    input.onkeydown = (e) => {
        if (!isGameActive) return;
        const now = performance.now();
        keyDownTimestamps[e.code] = now;
        if (lastKeyDownTime !== null) {
            downDownTimes.push(now - lastKeyDownTime);
        }
        lastKeyDownTime = now;
    };
    input.onkeyup = (e) => {
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
    };
    document.getElementById('identifyBtn').onclick = () => {
        const val = input.value;
        if (val !== promptText) {
            showNotification('Please type the prompt exactly.', 'error');
            return;
        }
        if (holdTimes.length < 5 || flightTimes.length < 4 || downDownTimes.length < 4) {
            showNotification('Please type more characters for accurate identification.', 'error');
            return;
        }
        document.getElementById('loading').style.display = 'block';
        document.getElementById('identifyBtn').disabled = true;
        fetch('/identify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hold_times: holdTimes,
                flight_times: flightTimes,
                down_down_times: downDownTimes,
                text: promptText
            })
        })
        .then(res => res.json())
        .then(res => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('identifyBtn').disabled = false;
            showResult(res);
        })
        .catch(err => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('identifyBtn').disabled = false;
            showNotification('Error identifying user.', 'error');
        });
    };
    function showResult(data) {
        const resultContainer = document.getElementById('result');
        resultContainer.style.display = 'block';
        const confidenceClass = data.confidence >= 0.8 ? 'confidence-high' : 
                              data.confidence >= 0.6 ? 'confidence-medium' : 'confidence-low';
        const resultHTML = `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">${data.user}</div>
                    <span class="confidence-score ${confidenceClass}">
                        Confidence: ${(data.confidence * 100).toFixed(1)}%
                    </span>
                </div>
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <div class="analysis-value">${data.analysis.avg_hold.toFixed(1)}ms</div>
                        <div class="analysis-label">Avg Hold</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${data.analysis.avg_flight.toFixed(1)}ms</div>
                        <div class="analysis-label">Avg Flight</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${data.analysis.avg_dd.toFixed(1)}ms</div>
                        <div class="analysis-label">Avg Down-Down</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${data.analysis.similarity_score.toFixed(3)}</div>
                        <div class="analysis-label">Similarity</div>
                    </div>
                </div>
                ${data.all_matches ? `
                    <div class="comparison-table">
                        <div class="table-header">All Matches</div>
                        ${data.all_matches.map(match => `
                            <div class="table-row">
                                <div class="user-name">${match.user}</div>
                                <div class="similarity-score">${(match.similarity * 100).toFixed(1)}%</div>
                                <div class="analysis-label">${match.method}</div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        resultContainer.innerHTML = resultHTML;
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
}); 