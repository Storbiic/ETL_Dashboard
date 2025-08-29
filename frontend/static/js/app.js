// ETL Dashboard JavaScript Application

// Global variables
let currentFileId = null;
let currentStep = 1;
let uploadedSheets = [];

// API base URL (will be set from template)
const FASTAPI_URL = window.FASTAPI_URL || 'http://127.0.0.1:8000';
console.log('FASTAPI_URL set to:', FASTAPI_URL);

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing application...');
    initializeUpload();
    initializeSheetSelection();
    console.log('Application initialized');
});

// File Upload Functions
function initializeUpload() {
    console.log('Initializing upload functionality...');

    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const fileInfo = document.getElementById('file-info');
    const removeFileBtn = document.getElementById('remove-file');

    console.log('Elements found:', {
        fileInput: !!fileInput,
        uploadArea: !!uploadArea,
        fileInfo: !!fileInfo,
        removeFileBtn: !!removeFileBtn
    });

    if (!uploadArea) {
        console.error('Upload area not found!');
        return;
    }
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        console.log('Upload area clicked');
        fileInput.click();
    });
    
    // File selection
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
    
    // Remove file
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', removeFile);
    }
}

function handleFileSelect(event) {
    console.log('File selected:', event.target.files);
    const file = event.target.files[0];
    if (file) {
        console.log('File details:', file.name, file.size, file.type);
        uploadFile(file);
    } else {
        console.log('No file selected');
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    console.log('uploadFile called with:', file.name, file.size);
    console.log('Using FASTAPI_URL:', FASTAPI_URL);

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
        showToast('Please select an Excel file (.xlsx or .xls)', 'error');
        return;
    }

    // Show upload progress
    showUploadProgress();

    try {
        const formData = new FormData();
        formData.append('file', file);

        console.log('Sending request to:', '/api/upload');

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        console.log('Upload response:', result);

        // Store file info
        currentFileId = result.file_id;
        uploadedSheets = result.sheet_names;
        console.log('Stored file info:', { currentFileId, uploadedSheets });

        // Show file info
        showFileInfo(result);

        // Enable next step
        enableStep(2);
        populateSheetSelectors(result.sheet_names, result.detected_sheets);

        showToast('File uploaded successfully!', 'success');
        
    } catch (error) {
        console.error('Upload error:', error);
        showToast(`Upload failed: ${error.message}`, 'error');
        hideUploadProgress();
    }
}

function showUploadProgress() {
    document.getElementById('upload-area').classList.add('hidden');
    document.getElementById('upload-progress').classList.remove('hidden');
    
    // Simulate progress (in real implementation, you'd track actual progress)
    let progress = 0;
    const progressBar = document.getElementById('upload-progress-bar');
    
    const interval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        progressBar.style.width = `${progress}%`;
    }, 200);
}

function hideUploadProgress() {
    document.getElementById('upload-area').classList.remove('hidden');
    document.getElementById('upload-progress').classList.add('hidden');
    document.getElementById('upload-progress-bar').style.width = '0%';
}

function showFileInfo(fileInfo) {
    console.log('showFileInfo called with:', fileInfo);
    hideUploadProgress();

    const fileNameEl = document.getElementById('file-name');
    const fileDetailsEl = document.getElementById('file-details');
    const fileInfoEl = document.getElementById('file-info');

    console.log('Elements found:', {
        fileNameEl: !!fileNameEl,
        fileDetailsEl: !!fileDetailsEl,
        fileInfoEl: !!fileInfoEl
    });

    if (fileNameEl) fileNameEl.textContent = fileInfo.filename;
    if (fileDetailsEl) {
        fileDetailsEl.textContent =
            `${formatFileSize(fileInfo.file_size)} • ${fileInfo.sheet_names.length} sheets`;
    }

    if (fileInfoEl) fileInfoEl.classList.remove('hidden');
}

function removeFile() {
    if (currentFileId) {
        // Optionally delete file from server
        fetch(`${FASTAPI_URL}/api/upload/${currentFileId}`, {
            method: 'DELETE'
        }).catch(console.error);
    }
    
    // Reset UI
    currentFileId = null;
    uploadedSheets = [];
    document.getElementById('file-info').classList.add('hidden');
    document.getElementById('file-input').value = '';
    
    // Reset steps
    resetSteps();
    
    showToast('File removed', 'info');
}

// Sheet Selection Functions
function initializeSheetSelection() {
    const previewBtn = document.getElementById('preview-btn');
    const masterSelect = document.getElementById('master-sheet');
    const statusSelect = document.getElementById('status-sheet');
    
    if (!previewBtn) return;
    
    previewBtn.addEventListener('click', previewSheets);
    
    // Enable preview button when both sheets are selected
    [masterSelect, statusSelect].forEach(select => {
        if (select) {
            select.addEventListener('change', checkSheetSelection);
        }
    });
}

function populateSheetSelectors(sheetNames, detectedSheets = null) {
    const masterSelect = document.getElementById('master-sheet');
    const statusSelect = document.getElementById('status-sheet');

    if (!masterSelect || !statusSelect) return;

    // Clear existing options
    masterSelect.innerHTML = '<option value="">Select sheet...</option>';
    statusSelect.innerHTML = '<option value="">Select sheet...</option>';

    // Add sheet options
    sheetNames.forEach(sheet => {
        const option1 = new Option(sheet, sheet);
        const option2 = new Option(sheet, sheet);
        masterSelect.add(option1);
        statusSelect.add(option2);
    });

    // Handle auto-detection
    if (detectedSheets) {
        showAutoDetectionResults(detectedSheets);

        // Auto-select detected sheets if confidence is high
        if (detectedSheets.masterbom && detectedSheets.confidence?.masterbom >= 0.7) {
            masterSelect.value = detectedSheets.masterbom;
        }
        if (detectedSheets.status && detectedSheets.confidence?.status >= 0.7) {
            statusSelect.value = detectedSheets.status;
        }

        // Check if both sheets are auto-selected
        checkSheetSelection();
    }

    // Show sheet selection section
    document.getElementById('sheet-selection').classList.remove('hidden');
}

function showAutoDetectionResults(detectedSheets) {
    // Create or update auto-detection info panel
    let infoPanel = document.getElementById('auto-detection-info');
    if (!infoPanel) {
        infoPanel = document.createElement('div');
        infoPanel.id = 'auto-detection-info';
        infoPanel.className = 'bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4';

        const sheetSelection = document.getElementById('sheet-selection');
        sheetSelection.insertBefore(infoPanel, sheetSelection.firstChild);
    }

    let html = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <i class="fas fa-magic text-blue-600 text-lg"></i>
            </div>
            <div class="ml-3 flex-1">
                <h4 class="text-sm font-medium text-blue-900 mb-2">Auto-Detection Results</h4>
                <div class="space-y-2">
    `;

    // Show MasterBOM detection
    if (detectedSheets.masterbom) {
        const confidence = Math.round((detectedSheets.confidence?.masterbom || 0) * 100);
        const confidenceColor = confidence >= 70 ? 'text-green-600' : confidence >= 50 ? 'text-yellow-600' : 'text-red-600';
        html += `
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-700">
                    <i class="fas fa-cogs mr-1"></i>
                    MasterBOM Sheet: <strong>${detectedSheets.masterbom}</strong>
                </span>
                <span class="${confidenceColor} font-medium">${confidence}% confidence</span>
            </div>
        `;
    } else {
        html += `
            <div class="text-sm text-gray-500">
                <i class="fas fa-exclamation-triangle mr-1"></i>
                No MasterBOM sheet detected - please select manually
            </div>
        `;
    }

    // Show Status detection
    if (detectedSheets.status) {
        const confidence = Math.round((detectedSheets.confidence?.status || 0) * 100);
        const confidenceColor = confidence >= 70 ? 'text-green-600' : confidence >= 50 ? 'text-yellow-600' : 'text-red-600';
        html += `
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-700">
                    <i class="fas fa-chart-bar mr-1"></i>
                    Status Sheet: <strong>${detectedSheets.status}</strong>
                </span>
                <span class="${confidenceColor} font-medium">${confidence}% confidence</span>
            </div>
        `;
    } else {
        html += `
            <div class="text-sm text-gray-500">
                <i class="fas fa-exclamation-triangle mr-1"></i>
                No Status sheet detected - please select manually
            </div>
        `;
    }

    html += `
                </div>
                <div class="mt-3 text-xs text-blue-700">
                    <i class="fas fa-info-circle mr-1"></i>
                    Auto-detected sheets are pre-selected. You can change them if needed.
                </div>
            </div>
        </div>
    `;

    infoPanel.innerHTML = html;
}

function checkSheetSelection() {
    const masterSheet = document.getElementById('master-sheet').value;
    const statusSheet = document.getElementById('status-sheet').value;
    const previewBtn = document.getElementById('preview-btn');
    
    if (masterSheet && statusSheet && masterSheet !== statusSheet) {
        previewBtn.disabled = false;
        enableStep(2);
    } else {
        previewBtn.disabled = true;
    }
}

function previewSheets() {
    const masterSheet = document.getElementById('master-sheet').value;
    const statusSheet = document.getElementById('status-sheet').value;
    
    if (!masterSheet || !statusSheet) {
        showToast('Please select both sheets', 'error');
        return;
    }
    
    if (masterSheet === statusSheet) {
        showToast('Please select different sheets', 'error');
        return;
    }
    
    // Navigate to profile page with both sheets
    window.location.href = `/profile?file_id=${currentFileId}&master_sheet=${encodeURIComponent(masterSheet)}&status_sheet=${encodeURIComponent(statusSheet)}`;
}

// Step Management Functions
function enableStep(stepNumber) {
    const stepElement = document.getElementById(`step-${stepNumber}`);
    const prevStepElement = document.getElementById(`step-${stepNumber - 1}`);
    
    if (stepElement) {
        stepElement.classList.remove('bg-gray-300', 'text-gray-600');
        stepElement.classList.add('bg-blue-600', 'text-white');
        
        // Update text colors
        const stepContainer = stepElement.parentElement.parentElement;
        const title = stepContainer.querySelector('h3');
        const subtitle = stepContainer.querySelector('p');
        
        if (title) {
            title.classList.remove('text-gray-500');
            title.classList.add('text-gray-900');
        }
        if (subtitle) {
            subtitle.classList.remove('text-gray-400');
            subtitle.classList.add('text-gray-500');
        }
    }
    
    // Mark previous step as completed
    if (prevStepElement && stepNumber > 1) {
        prevStepElement.classList.remove('bg-blue-600');
        prevStepElement.classList.add('bg-green-600');
        prevStepElement.innerHTML = '<i class="fas fa-check"></i>';
    }
    
    // Update progress bar
    if (stepNumber > 1) {
        const progressBar = document.getElementById(`progress-${stepNumber - 1}-${stepNumber}`);
        if (progressBar) {
            progressBar.style.width = '100%';
        }
    }
    
    currentStep = stepNumber;

    // Show/hide sections based on step
    showStepSection(stepNumber);
}

function showStepSection(stepNumber) {
    // Hide all sections first
    const sections = ['sheet-selection', 'preview-section', 'profile-section', 'transform-section'];
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('hidden');
        }
    });

    // Show the appropriate section
    let sectionToShow = '';
    switch(stepNumber) {
        case 2:
            sectionToShow = 'sheet-selection';
            break;
        case 3:
            sectionToShow = 'preview-section';
            break;
        case 4:
            sectionToShow = 'transform-section';
            updateTransformSection();
            break;
    }

    if (sectionToShow) {
        const section = document.getElementById(sectionToShow);
        if (section) {
            section.classList.remove('hidden');
        }
    }
}

function updateTransformSection() {
    const masterSelect = document.getElementById('master-sheet-select');
    const statusSelect = document.getElementById('status-sheet-select');

    const masterSheetDisplay = document.getElementById('selected-master-sheet');
    const statusSheetDisplay = document.getElementById('selected-status-sheet');

    if (masterSelect && masterSheetDisplay) {
        masterSheetDisplay.textContent = masterSelect.value || 'Not selected';
    }

    if (statusSelect && statusSheetDisplay) {
        statusSheetDisplay.textContent = statusSelect.value || 'Not selected';
    }
}

function resetSteps() {
    for (let i = 1; i <= 4; i++) {
        const stepElement = document.getElementById(`step-${i}`);
        if (stepElement) {
            stepElement.classList.remove('bg-blue-600', 'bg-green-600', 'text-white');
            stepElement.classList.add('bg-gray-300', 'text-gray-600');
            stepElement.textContent = i;
            
            // Reset text colors
            const stepContainer = stepElement.parentElement.parentElement;
            const title = stepContainer.querySelector('h3');
            const subtitle = stepContainer.querySelector('p');
            
            if (title) {
                title.classList.remove('text-gray-900');
                title.classList.add('text-gray-500');
            }
            if (subtitle) {
                subtitle.classList.remove('text-gray-500');
                subtitle.classList.add('text-gray-400');
            }
        }
        
        // Reset progress bars
        if (i < 4) {
            const progressBar = document.getElementById(`progress-${i}-${i + 1}`);
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }
    }
    
    // Enable first step
    enableStep(1);
    
    // Hide sections
    const sections = ['sheet-selection', 'preview-section', 'profile-section', 'transform-section'];
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('hidden');
        }
    });
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toast Notification System
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type} show`;
    
    const icon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="${icon} mr-2"></i>
            <span>${escapeHtml(message)}</span>
            <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(container);
    return container;
}

// Loading Overlay
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.querySelector('span').textContent = message;
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// Transform Functions
async function runTransform() {
    console.log('🔧 Starting ETL Transform...');

    if (!currentFileId) {
        showToast('No file uploaded. Please upload a file first.', 'error');
        return;
    }

    // Get selected sheets
    const masterSheet = document.getElementById('master-sheet-select')?.value;
    const statusSheet = document.getElementById('status-sheet-select')?.value;

    if (!masterSheet || !statusSheet) {
        showToast('Please select both master and status sheets.', 'error');
        return;
    }

    console.log('Transform parameters:', {
        fileId: currentFileId,
        masterSheet,
        statusSheet
    });

    // Show progress modal
    showProgressModal();

    try {
        const transformRequest = {
            file_id: currentFileId,
            master_sheet: masterSheet,
            status_sheet: statusSheet,
            options: {
                id_col: "Part ID",  // Default ID column
                date_cols: []       // Will be auto-detected
            }
        };

        console.log('Sending transform request:', transformRequest);

        // Start progress simulation
        startProgressSimulation();

        const response = await fetch('/api/transform', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transformRequest)
        });

        console.log('Transform response status:', response.status);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error || 'Transform failed');
        }

        const result = await response.json();
        console.log('Transform result:', result);

        if (result.success) {
            // Complete progress
            completeProgress();

            // Store result in sessionStorage for results page
            sessionStorage.setItem(`transform_result_${currentFileId}`, JSON.stringify(result));

            showToast('ETL transformation completed successfully!', 'success');

            // Redirect to results page after a short delay
            setTimeout(() => {
                hideProgressModal();
                window.location.href = `/results?file_id=${currentFileId}`;
            }, 2000);
        } else {
            throw new Error(result.error || 'Transform failed');
        }

    } catch (error) {
        console.error('Transform error:', error);
        hideProgressModal();
        showToast(`Transform failed: ${error.message}`, 'error');
    }
}

// Progress Modal Functions
let progressTimer = null;
let progressStartTime = null;
let currentProgressStep = 0;

const progressSteps = [
    { title: "Initializing transformation", description: "Setting up processing environment and validating input files..." },
    { title: "Reading Excel sheets", description: "Loading MasterBOM and Status sheets from uploaded file..." },
    { title: "Cleaning column headers", description: "Standardizing column names and removing special characters..." },
    { title: "Validating data structure", description: "Checking data integrity and identifying key columns..." },
    { title: "Processing MasterBOM data", description: "Cleaning part numbers and standardizing item descriptions..." },
    { title: "Calculating plant-item-status", description: "Creating normalized plant-item-status relationships..." },
    { title: "Resolving duplicates", description: "Applying Morocco supplier prioritization rules..." },
    { title: "Merging data tables", description: "Combining MasterBOM and Status data with proper joins..." },
    { title: "Generating fact tables", description: "Creating fact_parts table with dimensional relationships..." },
    { title: "Creating dimension tables", description: "Building date dimensions and lookup tables..." },
    { title: "Exporting processed files", description: "Saving CSV and Parquet files for analysis..." },
    { title: "Finalizing transformation", description: "Completing data validation and generating summary..." }
];

function showProgressModal() {
    const modal = document.getElementById('progress-modal');
    if (modal) {
        modal.classList.remove('hidden');
        progressStartTime = Date.now();
        currentProgressStep = 0;

        // Start timer
        progressTimer = setInterval(updateProgressTimer, 1000);

        // Initialize progress display
        updateProgressDisplay(0);
        initializeProgressSteps();
    }
}

function hideProgressModal() {
    const modal = document.getElementById('progress-modal');
    if (modal) {
        modal.classList.add('hidden');

        // Clear timer
        if (progressTimer) {
            clearInterval(progressTimer);
            progressTimer = null;
        }
    }
}

function updateProgressTimer() {
    if (!progressStartTime) return;

    const elapsed = Math.floor((Date.now() - progressStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    const timerElement = document.getElementById('progress-timer');
    if (timerElement) {
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

function updateProgressDisplay(percentage) {
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');

    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }

    if (progressPercentage) {
        progressPercentage.textContent = `${Math.round(percentage)}%`;
    }
}

function initializeProgressSteps() {
    const stepsContainer = document.getElementById('progress-steps');
    if (!stepsContainer) return;

    stepsContainer.innerHTML = '';

    progressSteps.forEach((step, index) => {
        const stepElement = document.createElement('div');
        stepElement.id = `progress-step-${index}`;
        stepElement.className = 'flex items-start space-x-3 p-3 rounded-lg transition-all duration-300';

        stepElement.innerHTML = `
            <div class="flex-shrink-0 mt-1">
                <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center">
                    <i class="fas fa-circle text-gray-300 text-xs"></i>
                </div>
            </div>
            <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900">${step.title}</div>
                <div class="text-xs text-gray-500 mt-1">${step.description}</div>
            </div>
        `;

        stepsContainer.appendChild(stepElement);
    });
}

function startProgressSimulation() {
    let progress = 0;
    const totalSteps = progressSteps.length;
    const stepDuration = 2000; // 2 seconds per step

    const progressInterval = setInterval(() => {
        if (currentProgressStep < totalSteps) {
            // Update current step
            updateProgressStep(currentProgressStep, 'active');

            // Calculate progress
            progress = ((currentProgressStep + 1) / totalSteps) * 90; // Leave 10% for completion
            updateProgressDisplay(progress);

            currentProgressStep++;
        } else {
            clearInterval(progressInterval);
        }
    }, stepDuration);
}

function updateProgressStep(stepIndex, status) {
    const stepElement = document.getElementById(`progress-step-${stepIndex}`);
    if (!stepElement) return;

    const icon = stepElement.querySelector('i');
    const circle = stepElement.querySelector('.w-6');

    switch (status) {
        case 'active':
            stepElement.className = 'flex items-start space-x-3 p-3 rounded-lg bg-blue-50 border border-blue-200 transition-all duration-300';
            circle.className = 'w-6 h-6 rounded-full border-2 border-blue-500 bg-blue-500 flex items-center justify-center';
            icon.className = 'fas fa-spinner fa-spin text-white text-xs';
            break;
        case 'completed':
            stepElement.className = 'flex items-start space-x-3 p-3 rounded-lg bg-green-50 border border-green-200 transition-all duration-300';
            circle.className = 'w-6 h-6 rounded-full border-2 border-green-500 bg-green-500 flex items-center justify-center';
            icon.className = 'fas fa-check text-white text-xs';
            break;
        case 'pending':
        default:
            stepElement.className = 'flex items-start space-x-3 p-3 rounded-lg transition-all duration-300';
            circle.className = 'w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center';
            icon.className = 'fas fa-circle text-gray-300 text-xs';
            break;
    }
}

function completeProgress() {
    // Mark all steps as completed
    for (let i = 0; i < progressSteps.length; i++) {
        updateProgressStep(i, 'completed');
    }

    // Set progress to 100%
    updateProgressDisplay(100);

    // Update modal header
    const header = document.querySelector('#progress-modal h3');
    if (header) {
        header.innerHTML = '<i class="fas fa-check-circle mr-2 text-green-400"></i>ETL Transformation Complete';
    }
}

// Export functions for use in templates
window.ETLDashboard = {
    showToast,
    showLoading,
    hideLoading,
    formatFileSize,
    escapeHtml,
    enableStep,
    resetSteps,
    runTransform,
    showProgressModal,
    hideProgressModal
};
