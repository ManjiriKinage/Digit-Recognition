// Handwritten Digit Recognition - Interactive Canvas & Inference Engine

document.addEventListener('DOMContentLoaded', () => {
    // Canvas & UI Elements
    const canvas = document.getElementById('paintCanvas');
    const ctx = canvas.getContext('2d');
    const clearBtn = document.getElementById('clearBtn');
    const eraserBtn = document.getElementById('eraserBtn');
    const brushSizeInput = document.getElementById('brushSize');
    const brushSizeLabel = document.getElementById('brushSizeLabel');
    const predictBtn = document.getElementById('predictBtn');
    const autoPredictToggle = document.getElementById('autoPredictToggle');
    const canvasHint = document.getElementById('canvasHint');
    
    // Tabs & Upload Elements
    const tabDraw = document.getElementById('tabDraw');
    const tabUpload = document.getElementById('tabUpload');
    const drawSection = document.getElementById('drawSection');
    const uploadSection = document.getElementById('uploadSection');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadPreviewContainer = document.getElementById('uploadPreviewContainer');
    const uploadImgPreview = document.getElementById('uploadImgPreview');
    const uploadFileName = document.getElementById('uploadFileName');
    const uploadFileSize = document.getElementById('uploadFileSize');
    const removeUploadBtn = document.getElementById('removeUploadBtn');

    // Prediction Output Elements
    const predictedDigit = document.getElementById('predictedDigit');
    const predictionHeading = document.getElementById('predictionHeading');
    const confidenceText = document.getElementById('confidenceText');
    const confidencePill = document.getElementById('confidencePill');
    const latencyBadge = document.getElementById('latencyBadge');
    const processedPreview = document.getElementById('processedPreview');
    const processedPlaceholder = document.getElementById('processedPlaceholder');
    const digitGlow = document.getElementById('digitGlow');
    const probabilityContainer = document.getElementById('probabilityContainer');
    const historyList = document.getElementById('historyList');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const presetButtons = document.querySelectorAll('.preset-btn');

    // State Variables
    let isDrawing = false;
    let isEraser = false;
    let brushSize = parseInt(brushSizeInput.value, 10);
    let hasDrawn = false;
    let autoPredictTimer = null;
    let currentUploadedFile = null;
    let lastX = 0;
    let lastY = 0;

    // Initialize Canvas
    function initCanvas() {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = brushSize;
    }

    initCanvas();
    renderInitialProbabilities();

    // Canvas Event Listeners
    function startDrawing(e) {
        isDrawing = true;
        hasDrawn = true;
        canvasHint.classList.add('opacity-0');
        
        const { x, y } = getCoordinates(e);
        lastX = x;
        lastY = y;
        
        ctx.beginPath();
        ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
        ctx.fillStyle = isEraser ? '#000000' : '#ffffff';
        ctx.fill();
        
        ctx.beginPath();
        ctx.moveTo(x, y);
    }

    function draw(e) {
        if (!isDrawing) return;
        e.preventDefault();
        
        const { x, y } = getCoordinates(e);
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = isEraser ? '#000000' : '#ffffff';
        ctx.lineWidth = brushSize;
        ctx.stroke();
        
        lastX = x;
        lastY = y;
    }

    function stopDrawing() {
        if (!isDrawing) return;
        isDrawing = false;
        ctx.closePath();
        
        if (autoPredictToggle.checked && hasDrawn) {
            clearTimeout(autoPredictTimer);
            autoPredictTimer = setTimeout(triggerCanvasPrediction, 250);
        }
    }

    function getCoordinates(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0].clientY);
        
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        
        return {
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY
        };
    }

    // Mouse Events
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    window.addEventListener('mouseup', stopDrawing);

    // Touch Events for Mobile / Tablets
    canvas.addEventListener('touchstart', startDrawing, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    window.addEventListener('touchend', stopDrawing);

    // Tool Controls
    eraserBtn.addEventListener('click', () => {
        isEraser = !isEraser;
        eraserBtn.classList.toggle('active', isEraser);
        eraserBtn.classList.toggle('border-brand-500', isEraser);
    });

    clearBtn.addEventListener('click', () => {
        clearCanvas();
        resetPredictionDisplay();
    });

    function clearCanvas() {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        hasDrawn = false;
        canvasHint.classList.remove('opacity-0');
    }

    brushSizeInput.addEventListener('input', (e) => {
        brushSize = parseInt(e.target.value, 10);
        brushSizeLabel.textContent = `${brushSize}px`;
    });

    // Preset Digit Drawers
    presetButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const digit = parseInt(btn.getAttribute('data-digit'), 10);
            drawPresetDigit(digit);
        });
    });

    function drawPresetDigit(digit) {
        clearCanvas();
        hasDrawn = true;
        canvasHint.classList.add('opacity-0');
        
        ctx.save();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 200px "Outfit", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(digit.toString(), canvas.width / 2, canvas.height / 2 + 10);
        ctx.restore();
        
        triggerCanvasPrediction();
    }

    // Tab Switching
    tabDraw.addEventListener('click', () => {
        tabDraw.classList.add('active');
        tabDraw.classList.remove('text-slate-400');
        tabUpload.classList.remove('active');
        tabUpload.classList.add('text-slate-400');
        drawSection.classList.remove('hidden');
        drawSection.classList.add('flex');
        uploadSection.classList.add('hidden');
        uploadSection.classList.remove('flex');
    });

    tabUpload.addEventListener('click', () => {
        tabUpload.classList.add('active');
        tabUpload.classList.remove('text-slate-400');
        tabDraw.classList.remove('active');
        tabDraw.classList.add('text-slate-400');
        uploadSection.classList.remove('hidden');
        uploadSection.classList.add('flex');
        drawSection.classList.add('hidden');
        drawSection.classList.remove('flex');
    });

    // File Upload / Dropzone
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-brand-500', 'bg-slate-800/80');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-brand-500', 'bg-slate-800/80');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-brand-500', 'bg-slate-800/80');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    function handleFileUpload(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file.');
            return;
        }

        currentUploadedFile = file;
        uploadFileName.textContent = file.name;
        uploadFileSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;

        const reader = new FileReader();
        reader.onload = (e) => {
            uploadImgPreview.src = e.target.result;
            uploadPreviewContainer.classList.remove('hidden');
            triggerImagePrediction(file);
        };
        reader.readAsDataURL(file);
    }

    removeUploadBtn.addEventListener('click', () => {
        currentUploadedFile = null;
        fileInput.value = '';
        uploadPreviewContainer.classList.add('hidden');
        resetPredictionDisplay();
    });

    // Prediction Dispatchers
    predictBtn.addEventListener('click', () => {
        if (drawSection.classList.contains('hidden')) {
            if (currentUploadedFile) {
                triggerImagePrediction(currentUploadedFile);
            } else {
                alert('Please upload an image first.');
            }
        } else {
            triggerCanvasPrediction();
        }
    });

    async function triggerCanvasPrediction() {
        if (!hasDrawn) return;
        
        const base64Image = canvas.toDataURL('image/png');
        const startTime = performance.now();

        try {
            setLoadingState(true);
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64Image })
            });

            const data = await response.json();
            const latency = Math.round(performance.now() - startTime);
            handlePredictionResponse(data, latency);
        } catch (err) {
            console.error('Prediction request failed:', err);
            predictionHeading.textContent = 'Server Error';
        } finally {
            setLoadingState(false);
        }
    }

    async function triggerImagePrediction(file) {
        const formData = new FormData();
        formData.append('file', file);
        const startTime = performance.now();

        try {
            setLoadingState(true);
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            const latency = Math.round(performance.now() - startTime);
            handlePredictionResponse(data, latency);
        } catch (err) {
            console.error('Upload prediction failed:', err);
            predictionHeading.textContent = 'Server Error';
        } finally {
            setLoadingState(false);
        }
    }

    function handlePredictionResponse(data, latency) {
        if (!data.success) {
            predictionHeading.textContent = data.error || 'Prediction Failed';
            predictedDigit.textContent = '?';
            confidenceText.textContent = 'Confidence: --%';
            return;
        }

        // Update Hero Card
        predictedDigit.textContent = data.digit;
        predictionHeading.textContent = `Identified as Digit "${data.digit}"`;
        confidenceText.textContent = `${data.confidence}% Confidence`;
        latencyBadge.textContent = `${latency} ms`;

        // Update Confidence Pill Styling
        if (data.confidence >= 90) {
            confidencePill.className = 'px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/50 text-xs font-semibold text-emerald-300 flex items-center gap-1.5';
            digitGlow.className = 'absolute -inset-2 bg-gradient-to-r from-emerald-500 to-accent-cyan rounded-3xl blur-xl opacity-50 transition-all duration-500';
        } else if (data.confidence >= 70) {
            confidencePill.className = 'px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/50 text-xs font-semibold text-amber-300 flex items-center gap-1.5';
            digitGlow.className = 'absolute -inset-2 bg-gradient-to-r from-amber-500 to-orange-500 rounded-3xl blur-xl opacity-50 transition-all duration-500';
        } else {
            confidencePill.className = 'px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/50 text-xs font-semibold text-rose-300 flex items-center gap-1.5';
            digitGlow.className = 'absolute -inset-2 bg-gradient-to-r from-rose-500 to-red-600 rounded-3xl blur-xl opacity-50 transition-all duration-500';
        }

        // Update 28x28 Preprocessed Preview
        if (data.processed_image) {
            processedPreview.src = data.processed_image;
            processedPreview.classList.remove('hidden');
            processedPlaceholder.classList.add('hidden');
        }

        // Update Probability Bars
        renderProbabilityBars(data.probabilities);

        // Append to History
        addToHistory(data.digit, data.confidence);
    }

    function renderInitialProbabilities() {
        const dummy = Array.from({ length: 10 }, (_, i) => ({
            digit: i,
            percentage: 0.0,
            is_predicted: false
        }));
        renderProbabilityBars(dummy);
    }

    function renderProbabilityBars(probabilities) {
        probabilityContainer.innerHTML = '';

        probabilities.forEach(item => {
            const isWinner = item.is_predicted;
            const row = document.createElement('div');
            row.className = `prob-row flex items-center gap-3 p-1.5 px-2.5 rounded-xl border border-transparent ${isWinner ? 'winner' : ''}`;

            const fillGradient = isWinner
                ? 'bg-gradient-to-r from-brand-500 to-accent-cyan shadow-sm shadow-brand-500/40'
                : 'bg-slate-700/80';

            const textStyle = isWinner
                ? 'text-brand-400 font-bold'
                : 'text-slate-400 font-semibold';

            const percentageStyle = isWinner
                ? 'text-white font-bold font-mono'
                : 'text-slate-400 font-mono';

            row.innerHTML = `
                <span class="w-5 text-center text-sm font-mono ${textStyle}">${item.digit}</span>
                <div class="flex-1 h-3 bg-slate-800/90 rounded-full overflow-hidden p-0.5 border border-slate-700/60">
                    <div class="prob-bar-fill h-full rounded-full ${fillGradient}" style="width: ${Math.max(item.percentage, 0.5)}%"></div>
                </div>
                <span class="w-14 text-right text-xs ${percentageStyle}">${item.percentage.toFixed(1)}%</span>
            `;

            probabilityContainer.appendChild(row);
        });
    }

    function addToHistory(digit, confidence) {
        if (historyList.querySelector('span.italic')) {
            historyList.innerHTML = '';
        }

        const chip = document.createElement('div');
        chip.className = 'flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-xs font-mono animate-fade-in';
        chip.innerHTML = `
            <span class="font-bold text-brand-400 text-sm">${digit}</span>
            <span class="text-[10px] text-slate-400">(${confidence.toFixed(0)}%)</span>
        `;

        historyList.prepend(chip);

        // Keep maximum 8 history items
        while (historyList.children.length > 8) {
            historyList.removeChild(historyList.lastChild);
        }
    }

    clearHistoryBtn.addEventListener('click', () => {
        historyList.innerHTML = '<span class="text-xs text-slate-600 italic">No predictions yet in this session.</span>';
    });

    function resetPredictionDisplay() {
        predictedDigit.textContent = '?';
        predictionHeading.textContent = 'Ready for input';
        confidenceText.textContent = 'Confidence: --%';
        confidencePill.className = 'px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-400 flex items-center gap-1.5';
        latencyBadge.textContent = '-- ms';
        processedPreview.classList.add('hidden');
        processedPlaceholder.classList.remove('hidden');
        digitGlow.className = 'absolute -inset-2 bg-gradient-to-r from-brand-500 to-accent-cyan rounded-3xl blur-xl opacity-30 transition-all duration-500';
        renderInitialProbabilities();
    }

    function setLoadingState(loading) {
        if (loading) {
            predictedDigit.classList.add('animate-pulse');
        } else {
            predictedDigit.classList.remove('animate-pulse');
        }
    }
});
