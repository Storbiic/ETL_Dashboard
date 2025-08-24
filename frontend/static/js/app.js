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
        populateSheetSelectors(result.sheet_names);

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

function populateSheetSelectors(sheetNames) {
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
    
    // Show sheet selection section
    document.getElementById('sheet-selection').classList.remove('hidden');
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

    // Show loading
    showLoading('Running ETL transformation...');

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
            // Store result in sessionStorage for results page
            sessionStorage.setItem(`transform_result_${currentFileId}`, JSON.stringify(result));

            showToast('ETL transformation completed successfully!', 'success');

            // Redirect to results page
            setTimeout(() => {
                window.location.href = `/results?file_id=${currentFileId}`;
            }, 1500);
        } else {
            throw new Error(result.error || 'Transform failed');
        }

    } catch (error) {
        console.error('Transform error:', error);
        showToast(`Transform failed: ${error.message}`, 'error');
    } finally {
        hideLoading();
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
    runTransform
};
