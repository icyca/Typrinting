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
    
    // N-gram data collection (same as typing game)
    let ngramData = { digraphs: {}, trigraphs: {} };
    let currentKeystrokeSequence = [];
    let lastKeystrokeTime = null;

    // Method selection handling
    const methodSelect = document.getElementById('methodSelect');
    const methodDescription = document.getElementById('methodDescription');
    
    const methodDescriptions = {
        'statistical': 'Uses mean and standard deviation of hold, flight, and down-down times. Best for same text.',
        'ngram': 'Analyzes timing patterns between character pairs and triplets. Works well with different texts.',
        'ml': 'Uses machine learning (KNN/SVM) on n-gram features. Most accurate but requires more training data.'
    };
    
    methodSelect.addEventListener('change', function() {
        const selectedMethod = this.value;
        methodDescription.textContent = methodDescriptions[selectedMethod] || '';
    });

    // N-gram extraction functions (same as typing game)
    function extractDigraphs(text) {
        const digraphs = [];
        for (let i = 0; i < text.length - 1; i++) {
            const digraph = text.substring(i, i + 2).toLowerCase();
            if (digraph.match(/[a-z]{2}/)) {
                digraphs.push(digraph);
            }
        }
        return digraphs;
    }

    function extractTrigraphs(text) {
        const trigraphs = [];
        for (let i = 0; i < text.length - 2; i++) {
            const trigraph = text.substring(i, i + 3).toLowerCase();
            if (trigraph.match(/[a-z]{3}/)) {
                trigraphs.push(trigraph);
            }
        }
        return trigraphs;
    }

    function addNgramTiming(ngram, timing) {
        if (!ngramData.digraphs[ngram]) {
            ngramData.digraphs[ngram] = [];
        }
        ngramData.digraphs[ngram].push(timing);
    }

    function addTrigraphTiming(trigraph, timing) {
        if (!ngramData.trigraphs[trigraph]) {
            ngramData.trigraphs[trigraph] = [];
        }
        ngramData.trigraphs[trigraph].push(timing);
    }

    function processNgrams() {
        // Process digraphs (2-grams)
        const digraphs = extractDigraphs(promptText);
        for (let i = 0; i < digraphs.length; i++) {
            const digraph = digraphs[i];
            const firstChar = digraph[0];
            const secondChar = digraph[1];
            
            let timing = null;
            for (let j = 0; j < currentKeystrokeSequence.length - 1; j++) {
                if (currentKeystrokeSequence[j].key === firstChar && 
                    currentKeystrokeSequence[j+1].key === secondChar &&
                    currentKeystrokeSequence[j].type === 'down' &&
                    currentKeystrokeSequence[j+1].type === 'down') {
                    timing = currentKeystrokeSequence[j+1].time - currentKeystrokeSequence[j].time;
                    break;
                }
            }
            if (timing !== null) {
                addNgramTiming(digraph, timing);
            }
        }
        
        // Process trigraphs (3-grams)
        const trigraphs = extractTrigraphs(promptText);
        for (let i = 0; i < trigraphs.length; i++) {
            const trigraph = trigraphs[i];
            const firstChar = trigraph[0];
            const secondChar = trigraph[1];
            const thirdChar = trigraph[2];
            
            let timing = null;
            for (let j = 0; j < currentKeystrokeSequence.length - 2; j++) {
                if (currentKeystrokeSequence[j].key === firstChar && 
                    currentKeystrokeSequence[j+1].key === secondChar &&
                    currentKeystrokeSequence[j+2].key === thirdChar &&
                    currentKeystrokeSequence[j].type === 'down' &&
                    currentKeystrokeSequence[j+1].type === 'down' &&
                    currentKeystrokeSequence[j+2].type === 'down') {
                    timing = currentKeystrokeSequence[j+2].time - currentKeystrokeSequence[j].time;
                    break;
                }
            }
            if (timing !== null) {
                addTrigraphTiming(trigraph, timing);
            }
        }
    }

    input.onkeydown = (e) => {
        if (!isGameActive) return;
        const now = performance.now();
        keyDownTimestamps[e.code] = now;
        if (lastKeyDownTime !== null) {
            downDownTimes.push(now - lastKeyDownTime);
        }
        lastKeyDownTime = now;
        
        // Track keystroke sequence for n-grams
        currentKeystrokeSequence.push({
            key: e.key.toLowerCase(),
            time: now,
            type: 'down'
        });
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
        
        // Track keystroke sequence for n-grams
        currentKeystrokeSequence.push({
            key: e.key.toLowerCase(),
            time: now,
            type: 'up'
        });
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
        
        // Process n-grams
        processNgrams();
        
        const selectedMethod = methodSelect.value;
        
        document.getElementById('loading').style.display = 'block';
        document.getElementById('identifyBtn').disabled = true;
        
        fetch('/identify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: selectedMethod,
                hold_times: holdTimes,
                flight_times: flightTimes,
                down_down_times: downDownTimes,
                text: promptText,
                ngram_data: ngramData,
                keystroke_sequence: currentKeystrokeSequence
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
        
        const confidenceClass = data.acceptance >= 0.8 ? 'confidence-high' : 
                              data.acceptance >= 0.6 ? 'confidence-medium' : 'confidence-low';
        
        let analysisHTML = '';
        if (data.analysis && Object.keys(data.analysis).length > 0) {
            analysisHTML = `
                <div class="analysis-grid">
                    ${data.analysis.avg_hold ? `
                        <div class="analysis-item">
                            <div class="analysis-value">${data.analysis.avg_hold.toFixed(1)}ms</div>
                            <div class="analysis-label">Avg Hold</div>
                        </div>
                    ` : ''}
                    ${data.analysis.avg_flight ? `
                        <div class="analysis-item">
                            <div class="analysis-value">${data.analysis.avg_flight.toFixed(1)}ms</div>
                            <div class="analysis-label">Avg Flight</div>
                        </div>
                    ` : ''}
                    ${data.analysis.avg_dd ? `
                        <div class="analysis-item">
                            <div class="analysis-value">${data.analysis.avg_dd.toFixed(1)}ms</div>
                            <div class="analysis-label">Avg Down-Down</div>
                        </div>
                    ` : ''}
                    <div class="analysis-item">
                        <div class="analysis-value">${(data.acceptance * 100).toFixed(1)}%</div>
                        <div class="analysis-label">Confidence</div>
                    </div>
                </div>
            `;
        } else {
            analysisHTML = `
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <div class="analysis-value">${(data.acceptance * 100).toFixed(1)}%</div>
                        <div class="analysis-label">Confidence</div>
                    </div>
                </div>
            `;
        }
        
        const resultHTML = `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">${data.user}</div>
                    <span class="confidence-score ${confidenceClass}">
                        Method: ${data.method || 'Unknown'} | Confidence: ${(data.acceptance * 100).toFixed(1)}%
                    </span>
                </div>
                ${analysisHTML}
                ${data.all_matches && data.all_matches.length > 0 ? `
                    <div class="comparison-table">
                        <div class="table-header">All Matches</div>
                        ${data.all_matches.map(match => `
                            <div class="table-row">
                                <div class="user-name">${match.user}</div>
                                <div class="similarity-score">${(match.acceptance * 100).toFixed(1)}%</div>
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