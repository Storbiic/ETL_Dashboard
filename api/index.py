"""Main index route - serves the frontend."""
from http.server import BaseHTTPRequestHandler
import os
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve the main dashboard page."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        # Add CSP header to prevent eval() while allowing inline scripts
        self.send_header('Content-Security-Policy', 
            "default-src 'self'; " +
            "script-src 'self' 'unsafe-inline'; " +
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; " +
            "font-src 'self' https://cdnjs.cloudflare.com; " +
            "img-src 'self' data: https:; " +
            "connect-src 'self'"
        )
        self.end_headers()
        
        # Get the current Vercel URL
        vercel_url = os.environ.get('VERCEL_URL', 'localhost:3000')
        if not vercel_url.startswith('http'):
            vercel_url = f"https://{vercel_url}"
        
        # Create a full HTML page with embedded CSS and JavaScript
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETL Dashboard</title>
    
    <!-- Tailwind CSS (production build) -->
    <style>
        /* Core Tailwind utilities for production */
        .hidden { display: none !important; }
        .block { display: block !important; }
        .flex { display: flex !important; }
        .grid { display: grid !important; }
        .relative { position: relative !important; }
        .absolute { position: absolute !important; }
        .w-full { width: 100% !important; }
        .h-full { height: 100% !important; }
        .max-w-4xl { max-width: 56rem !important; }
        .mx-auto { margin-left: auto !important; margin-right: auto !important; }
        .px-4 { padding-left: 1rem !important; padding-right: 1rem !important; }
        .py-8 { padding-top: 2rem !important; padding-bottom: 2rem !important; }
        .mb-8 { margin-bottom: 2rem !important; }
        .text-center { text-align: center !important; }
        .text-3xl { font-size: 1.875rem !important; line-height: 2.25rem !important; }
        .font-bold { font-weight: 700 !important; }
        .text-blue-600 { color: rgb(37 99 235) !important; }
        .text-gray-600 { color: rgb(75 85 99) !important; }
        .bg-white { background-color: rgb(255 255 255) !important; }
        .bg-blue-500 { background-color: rgb(59 130 246) !important; }
        .hover\\:bg-blue-600:hover { background-color: rgb(37 99 235) !important; }
        .text-white { color: rgb(255 255 255) !important; }
        .rounded-lg { border-radius: 0.5rem !important; }
        .border-2 { border-width: 2px !important; }
        .border-dashed { border-style: dashed !important; }
        .border-gray-300 { border-color: rgb(209 213 219) !important; }
        .p-8 { padding: 2rem !important; }
        .cursor-pointer { cursor: pointer !important; }
        .transition-all { transition-property: all !important; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important; transition-duration: 150ms !important; }
    </style>
    
    <!-- Font Awesome CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .upload-area:hover i {{
            color: #3b82f6;
        }}
        
        .step-container {{
            transition: all 0.3s ease;
        }}
        
        .progress-bar-animated {{
            background: linear-gradient(45deg, 
                rgba(59, 130, 246, 1) 0%, 
                rgba(16, 185, 129, 1) 50%,
                rgba(59, 130, 246, 1) 100%);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
        }}
        
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="flex items-center">
                        <i class="fas fa-database text-blue-600 text-2xl mr-3"></i>
                        <span class="text-xl font-semibold text-gray-900">ETL Dashboard</span>
                    </a>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/api/health" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-heart text-green-500"></i>
                        Health
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="space-y-8">
            <!-- Header -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-gray-900">Excel ETL Dashboard</h1>
                <p class="mt-2 text-lg text-gray-600">Upload, analyze, and transform Excel workbooks into Power BI-ready data</p>
            </div>

            <!-- Enhanced Progress Stepper -->
            <div class="bg-white rounded-lg shadow p-6">
                <!-- Overall Progress Bar -->
                <div class="mb-6">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-700" id="current-step-name">Step 1: Upload Excel Workbook</span>
                        <div class="flex items-center space-x-4">
                            <span class="text-sm text-gray-500" id="step-percentage">0% Complete</span>
                        </div>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div id="overall-progress" class="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out" style="width: 0%"></div>
                    </div>
                </div>

                <!-- Step Indicators -->
                <div class="flex items-center justify-between">
                    <div class="flex items-center step-container" data-step="1">
                        <div class="relative">
                            <div id="step-1" class="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300">
                                <i class="fas fa-upload"></i>
                            </div>
                            <div id="step-1-check" class="absolute inset-0 flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300 opacity-0 scale-0">
                                <i class="fas fa-check"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-medium text-gray-900">Upload</h3>
                            <p class="text-sm text-gray-500">Select Excel workbook</p>
                            <div id="step-1-status" class="text-xs text-blue-600 font-medium mt-1">Current</div>
                        </div>
                    </div>

                    <div class="flex-1 mx-4">
                        <div class="h-2 bg-gray-200 rounded-full">
                            <div id="progress-1-2" class="h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>

                    <div class="flex items-center step-container" data-step="2">
                        <div class="relative">
                            <div id="step-2" class="flex items-center justify-center w-12 h-12 bg-gray-300 text-gray-600 rounded-full font-semibold transition-all duration-300">
                                <i class="fas fa-table"></i>
                            </div>
                            <div id="step-2-check" class="absolute inset-0 flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300 opacity-0 scale-0">
                                <i class="fas fa-check"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-medium text-gray-500">Select & Preview</h3>
                            <p class="text-sm text-gray-400">Choose two sheets</p>
                            <div id="step-2-status" class="text-xs text-gray-400 font-medium mt-1">Pending</div>
                        </div>
                    </div>

                    <div class="flex-1 mx-4">
                        <div class="h-2 bg-gray-200 rounded-full">
                            <div id="progress-2-3" class="h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>

                    <div class="flex items-center step-container" data-step="3">
                        <div class="relative">
                            <div id="step-3" class="flex items-center justify-center w-12 h-12 bg-gray-300 text-gray-600 rounded-full font-semibold transition-all duration-300">
                                <i class="fas fa-chart-bar"></i>
                            </div>
                            <div id="step-3-check" class="absolute inset-0 flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300 opacity-0 scale-0">
                                <i class="fas fa-check"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-medium text-gray-500">Profile</h3>
                            <p class="text-sm text-gray-400">Analyze data quality</p>
                            <div id="step-3-status" class="text-xs text-gray-400 font-medium mt-1">Pending</div>
                        </div>
                    </div>

                    <div class="flex-1 mx-4">
                        <div class="h-2 bg-gray-200 rounded-full">
                            <div id="progress-3-4" class="h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>

                    <div class="flex items-center step-container" data-step="4">
                        <div class="relative">
                            <div id="step-4" class="flex items-center justify-center w-12 h-12 bg-gray-300 text-gray-600 rounded-full font-semibold transition-all duration-300">
                                <i class="fas fa-cogs"></i>
                            </div>
                            <div id="step-4-check" class="absolute inset-0 flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300 opacity-0 scale-0">
                                <i class="fas fa-check"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-medium text-gray-500">Transform</h3>
                            <p class="text-sm text-gray-400">Run ETL process</p>
                            <div id="step-4-status" class="text-xs text-gray-400 font-medium mt-1">Pending</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Step 1: Upload -->
            <div id="upload-section" class="bg-white rounded-lg shadow p-6 fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-semibold text-gray-900">
                        <i class="fas fa-upload mr-2 text-blue-600"></i>
                        Step 1: Upload Excel Workbook
                    </h2>
                    <button id="show-logs-btn" class="text-gray-500 hover:text-gray-700 text-sm">
                        <i class="fas fa-terminal mr-1"></i>
                        Show Logs
                    </button>
                </div>

                <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-all duration-300 upload-area">
                    <input type="file" id="file-input" accept=".xlsx,.xls" class="hidden">
                    <div id="upload-area" class="cursor-pointer">
                        <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4 transition-colors"></i>
                        <p class="text-lg font-medium text-gray-900 mb-2">Drop your Excel file here or click to browse</p>
                        <p class="text-sm text-gray-500">Supports .xlsx and .xls files (max 50MB)</p>
                    </div>

                    <!-- Enhanced Upload Progress -->
                    <div id="upload-progress" class="hidden mt-6">
                        <div class="flex items-center justify-center mb-4">
                            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
                            <span class="text-lg font-medium text-gray-900">Uploading...</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-3">
                            <div id="upload-progress-bar" class="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-300" style="width: 0%"></div>
                        </div>
                        <div class="flex justify-between text-sm text-gray-600 mt-2">
                            <span id="upload-status">Preparing upload...</span>
                            <span id="upload-percentage">0%</span>
                        </div>
                    </div>

                    <!-- Processing State -->
                    <div id="processing-state" class="hidden mt-6">
                        <div class="flex items-center justify-center mb-4">
                            <div class="animate-pulse rounded-full h-8 w-8 bg-green-500 mr-3"></div>
                            <span class="text-lg font-medium text-green-700">Processing file...</span>
                        </div>
                        <div class="text-sm text-gray-600">Analyzing sheets and structure</div>
                    </div>
                </div>

                <!-- Enhanced File Info -->
                <div id="file-info" class="hidden mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
                                <i class="fas fa-file-excel text-green-600"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-900" id="file-name"></p>
                                <p class="text-sm text-gray-500" id="file-details"></p>
                                <div class="flex items-center mt-1">
                                    <i class="fas fa-check-circle text-green-500 text-xs mr-1"></i>
                                    <span class="text-xs text-green-600 font-medium">Upload successful</span>
                                </div>
                            </div>
                        </div>
                        <button id="remove-file" class="text-red-600 hover:text-red-800 p-2 rounded-full hover:bg-red-50 transition-colors">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>

                <!-- Upload Tips -->
                <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div class="flex items-start">
                        <i class="fas fa-lightbulb text-blue-500 mt-0.5 mr-2"></i>
                        <div class="text-sm text-blue-700">
                            <strong>Tips:</strong> Ensure your Excel file contains MasterBOM and Status sheets.
                            The system will auto-detect sheet names and help you select the correct ones.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Step 2: Sheet Selection -->
            <div id="sheet-selection" class="bg-white rounded-lg shadow p-6 hidden fade-in">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">
                    <i class="fas fa-table mr-2 text-blue-600"></i>
                    Step 2: Select Sheets
                </h2>

                <p class="text-gray-600 mb-6">Choose exactly two sheets: one for MasterBOM and one for Status data. Auto-detected sheets are pre-selected when possible.</p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-gray-700">
                            <i class="fas fa-cogs mr-1 text-blue-600"></i>
                            MasterBOM Sheet
                        </label>
                        <div class="relative">
                            <select id="master-sheet"
                                    class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                                    onchange="checkSheetSelection()">
                                <option value="">Select sheet...</option>
                            </select>
                            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                                <i class="fas fa-chevron-down text-gray-400"></i>
                            </div>
                        </div>
                        <div class="text-xs text-gray-500">
                            <i class="fas fa-info-circle mr-1"></i>
                            Contains parts, components, or bill of materials data
                        </div>
                    </div>

                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-gray-700">
                            <i class="fas fa-chart-bar mr-1 text-purple-600"></i>
                            Status Sheet
                        </label>
                        <div class="relative">
                            <select id="status-sheet"
                                    class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                                    onchange="checkSheetSelection()">
                                <option value="">Select sheet...</option>
                            </select>
                            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                                <i class="fas fa-chevron-down text-gray-400"></i>
                            </div>
                        </div>
                        <div class="text-xs text-gray-500">
                            <i class="fas fa-info-circle mr-1"></i>
                            Contains status, summary, or dashboard data
                        </div>
                    </div>
                </div>

                <!-- Selection Status Indicator -->
                <div id="selection-status" class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200 hidden">
                    <div class="flex items-center">
                        <i class="fas fa-check-circle text-green-500 mr-2"></i>
                        <span class="text-sm text-gray-700">Both sheets selected. Ready to preview!</span>
                    </div>
                </div>

                <div class="mt-6 flex justify-between items-center">
                    <div class="text-sm text-gray-500">
                        <i class="fas fa-magic mr-1"></i>
                        Auto-detection helps speed up your workflow
                    </div>
                    <button id="preview-btn"
                            class="bg-gray-400 text-white px-6 py-3 rounded-md font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                            disabled>
                        <i class="fas fa-eye mr-2"></i>
                        Preview Sheets
                    </button>
                </div>
            </div>

            <!-- Additional sections (initially hidden) -->
            <div id="preview-section" class="hidden">
                <!-- Preview content will be loaded here -->
            </div>

            <div id="profile-section" class="hidden">
                <!-- Profile content will be loaded here -->
            </div>

            <div id="transform-section" class="hidden bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">
                    <i class="fas fa-cogs mr-2 text-blue-600"></i>
                    Run ETL Transformation
                </h2>

                <div class="space-y-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <i class="fas fa-info-circle text-blue-400 text-xl"></i>
                            </div>
                            <div class="ml-3">
                                <h3 class="text-sm font-medium text-blue-800">Ready to Transform</h3>
                                <div class="mt-2 text-sm text-blue-700">
                                    Your Excel file has been analyzed and is ready for ETL processing.
                                    This will create Power BI-ready data tables and generate download files.
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="p-4 border border-gray-200 rounded-lg">
                            <h3 class="font-medium text-gray-900 mb-2">
                                <i class="fas fa-table mr-2 text-green-600"></i>
                                Master Sheet
                            </h3>
                            <p class="text-sm text-gray-600" id="selected-master-sheet">Not selected</p>
                        </div>

                        <div class="p-4 border border-gray-200 rounded-lg">
                            <h3 class="font-medium text-gray-900 mb-2">
                                <i class="fas fa-chart-bar mr-2 text-purple-600"></i>
                                Status Sheet
                            </h3>
                            <p class="text-sm text-gray-600" id="selected-status-sheet">Not selected</p>
                        </div>
                    </div>

                    <div class="flex justify-between items-center pt-4">
                        <button id="back-btn" class="text-blue-600 hover:text-blue-800 transition-colors">
                            <i class="fas fa-arrow-left mr-2"></i>
                            Back to Profile
                        </button>

                        <button id="run-transform-btn"
                                class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-md font-medium transition-all duration-200 transform hover:scale-105">
                            <i class="fas fa-play mr-2"></i>
                            Run ETL Transform
                        </button>
                    </div>

                    <!-- Transform Progress Section -->
                    <div id="transform-progress" class="hidden mt-6 p-4 bg-gray-50 rounded-lg border">
                        <div class="flex items-center justify-between mb-3">
                            <h4 class="font-medium text-gray-900">ETL Processing</h4>
                        </div>

                        <div class="w-full bg-gray-200 rounded-full h-2 mb-3">
                            <div id="transform-progress-bar" class="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-300 progress-bar-animated" style="width: 0%"></div>
                        </div>

                        <div class="flex justify-between text-sm text-gray-600">
                            <span id="transform-status">Initializing...</span>
                            <span id="transform-percentage">0%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript -->
    <script>
        // Use current origin for API calls to avoid CORS issues
        const API_BASE_URL = window.location.origin;
        let currentStep = 1;
        let currentFileId = null;
        let uploadedSheets = [];
        let logEntries = [];
        let logPanelOpen = false;

        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM Content Loaded - Initializing application...');
            initializeUpload();
            initializeSheetSelection();
            initializeEventListeners();
            console.log('Application initialized');
        }});

        // File upload initialization
        function initializeUpload() {{
            const fileInput = document.getElementById('file-input');
            const uploadArea = document.getElementById('upload-area');
            
            if (fileInput && uploadArea) {{
                // Click to browse
                uploadArea.addEventListener('click', () => fileInput.click());
                
                // File selection
                fileInput.addEventListener('change', function(e) {{
                    const file = e.target.files[0];
                    if (file) {{
                        uploadFile(file);
                    }}
                }});

                // Drag and drop
                uploadArea.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.add('border-blue-400');
                }});

                uploadArea.addEventListener('dragleave', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.remove('border-blue-400');
                }});

                uploadArea.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.remove('border-blue-400');
                    const file = e.dataTransfer.files[0];
                    if (file) {{
                        uploadFile(file);
                    }}
                }});
            }}
        }}

        // Sheet selection initialization
        function initializeSheetSelection() {{
            // Sheet selection handlers will be added when sheets are loaded
        }}

        // Initialize event listeners for buttons (replacing onclick attributes)
        function initializeEventListeners() {{
            // Log panel toggle button
            const showLogsBtn = document.getElementById('show-logs-btn');
            if (showLogsBtn) {{
                showLogsBtn.addEventListener('click', toggleLogPanel);
            }}

            // Preview sheets button
            const previewBtn = document.getElementById('preview-btn');
            if (previewBtn) {{
                previewBtn.addEventListener('click', previewSheets);
            }}

            // Back button
            const backBtn = document.getElementById('back-btn');
            if (backBtn) {{
                backBtn.addEventListener('click', () => window.history.back());
            }}

            // Run transform button
            const runTransformBtn = document.getElementById('run-transform-btn');
            if (runTransformBtn) {{
                runTransformBtn.addEventListener('click', runTransform);
            }}
        }}

        // Log panel toggle
        function toggleLogPanel() {{
            // Simple log implementation for Vercel
            console.log('Log panel toggle requested');
        }}

        // Upload file function
        async function uploadFile(file) {{
            const uploadArea = document.getElementById('upload-area');
            const uploadProgress = document.getElementById('upload-progress');
            const processingState = document.getElementById('processing-state');
            const fileInfo = document.getElementById('file-info');

            try {{
                // Show upload progress
                uploadArea.classList.add('hidden');
                uploadProgress.classList.remove('hidden');

                const formData = new FormData();
                formData.append('file', file);

                // Simulate upload progress
                const progressBar = document.getElementById('upload-progress-bar');
                const uploadStatus = document.getElementById('upload-status');
                const uploadPercentage = document.getElementById('upload-percentage');

                for (let i = 0; i <= 90; i += 10) {{
                    progressBar.style.width = i + '%';
                    uploadPercentage.textContent = i + '%';
                    uploadStatus.textContent = i < 50 ? 'Uploading file...' : 'Processing upload...';
                    await new Promise(resolve => setTimeout(resolve, 200));
                }}

                // Make API call
                const response = await fetch(`${{API_BASE_URL}}/api/upload`, {{
                    method: 'POST',
                    body: formData
                }});

                if (response.ok) {{
                    const result = await response.json();
                    currentFileId = result.file_id;
                    uploadedSheets = result.sheets || [];

                    // Complete progress
                    progressBar.style.width = '100%';
                    uploadPercentage.textContent = '100%';
                    uploadStatus.textContent = 'Upload complete!';

                    await new Promise(resolve => setTimeout(resolve, 500));

                    // Hide progress, show processing
                    uploadProgress.classList.add('hidden');
                    processingState.classList.remove('hidden');

                    await new Promise(resolve => setTimeout(resolve, 1500));

                    // Show file info
                    processingState.classList.add('hidden');
                    showFileInfo(file, result);
                    
                    // Update step progress
                    updateStepProgress(1, 100);
                    
                    // Move to next step after delay
                    setTimeout(() => {{
                        moveToStep(2);
                        setupSheetSelection(uploadedSheets);
                    }}, 2000);

                }} else {{
                    throw new Error('Upload failed');
                }}
            }} catch (error) {{
                console.error('Upload error:', error);
                // Reset UI on error
                uploadArea.classList.remove('hidden');
                uploadProgress.classList.add('hidden');
                processingState.classList.add('hidden');
                alert('Upload failed. Please try again.');
            }}
        }}

        // Show file information
        function showFileInfo(file, result) {{
            const fileInfo = document.getElementById('file-info');
            const fileName = document.getElementById('file-name');
            const fileDetails = document.getElementById('file-details');

            if (fileInfo && fileName && fileDetails) {{
                fileName.textContent = file.name;
                fileDetails.textContent = `${{formatFileSize(file.size)}} • ${{uploadedSheets.length}} sheets detected`;
                fileInfo.classList.remove('hidden');

                // Remove file handler
                const removeBtn = document.getElementById('remove-file');
                if (removeBtn) {{
                    removeBtn.addEventListener('click', () => {{
                        fileInfo.classList.add('hidden');
                        document.getElementById('upload-area').classList.remove('hidden');
                        resetSteps();
                    }});
                }}
            }}
        }}

        // Format file size
        function formatFileSize(bytes) {{
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }}

        // Update step progress
        function updateStepProgress(stepNum, percentage) {{
            const progressBar = document.getElementById('overall-progress');
            const percentageText = document.getElementById('step-percentage');
            
            if (progressBar && percentageText) {{
                const totalProgress = ((stepNum - 1) * 25) + (percentage * 0.25);
                progressBar.style.width = totalProgress + '%';
                percentageText.textContent = Math.round(totalProgress) + '% Complete';
            }}
        }}

        // Move to step
        function moveToStep(stepNum) {{
            currentStep = stepNum;
            
            // Update step indicators
            for (let i = 1; i <= 4; i++) {{
                const stepElement = document.getElementById(`step-${{i}}`);
                const stepStatus = document.getElementById(`step-${{i}}-status`);
                const stepCheck = document.getElementById(`step-${{i}}-check`);
                
                if (stepElement && stepStatus) {{
                    if (i < stepNum) {{
                        // Completed step
                        stepElement.className = 'flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300';
                        stepStatus.textContent = 'Completed';
                        stepStatus.className = 'text-xs text-green-600 font-medium mt-1';
                        if (stepCheck) {{
                            stepCheck.style.opacity = '1';
                            stepCheck.style.transform = 'scale(1)';
                        }}
                    }} else if (i === stepNum) {{
                        // Current step
                        stepElement.className = 'flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full font-semibold shadow-lg transition-all duration-300';
                        stepStatus.textContent = 'Current';
                        stepStatus.className = 'text-xs text-blue-600 font-medium mt-1';
                    }} else {{
                        // Future step
                        stepElement.className = 'flex items-center justify-center w-12 h-12 bg-gray-300 text-gray-600 rounded-full font-semibold transition-all duration-300';
                        stepStatus.textContent = 'Pending';
                        stepStatus.className = 'text-xs text-gray-400 font-medium mt-1';
                    }}
                }}
            }}

            // Show/hide sections
            const sections = ['upload-section', 'sheet-selection', 'preview-section', 'profile-section', 'transform-section'];
            sections.forEach((sectionId, index) => {{
                const section = document.getElementById(sectionId);
                if (section) {{
                    if (index + 1 === stepNum) {{
                        section.classList.remove('hidden');
                    }} else {{
                        section.classList.add('hidden');
                    }}
                }}
            }});

            // Update step name
            const stepNames = [
                'Step 1: Upload Excel Workbook',
                'Step 2: Select & Preview Sheets',
                'Step 3: Profile Data Quality',
                'Step 4: Transform & Export'
            ];
            const stepNameElement = document.getElementById('current-step-name');
            if (stepNameElement) {{
                stepNameElement.textContent = stepNames[stepNum - 1] || 'Complete';
            }}
        }}

        // Setup sheet selection
        function setupSheetSelection(sheets) {{
            const masterSelect = document.getElementById('master-sheet');
            const statusSelect = document.getElementById('status-sheet');

            if (masterSelect && statusSelect && sheets) {{
                // Clear existing options
                masterSelect.innerHTML = '<option value="">Select sheet...</option>';
                statusSelect.innerHTML = '<option value="">Select sheet...</option>';

                // Add sheet options
                sheets.forEach(sheet => {{
                    const masterOption = document.createElement('option');
                    masterOption.value = sheet;
                    masterOption.textContent = sheet;
                    masterSelect.appendChild(masterOption);

                    const statusOption = document.createElement('option');
                    statusOption.value = sheet;
                    statusOption.textContent = sheet;
                    statusSelect.appendChild(statusOption);
                }});

                // Auto-detect sheets
                const masterDetected = sheets.find(s => s.toLowerCase().includes('master') || s.toLowerCase().includes('bom'));
                const statusDetected = sheets.find(s => s.toLowerCase().includes('status') || s.toLowerCase().includes('summary'));

                if (masterDetected) masterSelect.value = masterDetected;
                if (statusDetected) statusSelect.value = statusDetected;

                checkSheetSelection();
            }}
        }}

        // Check sheet selection
        function checkSheetSelection() {{
            const masterSelect = document.getElementById('master-sheet');
            const statusSelect = document.getElementById('status-sheet');
            const previewBtn = document.getElementById('preview-btn');
            const selectionStatus = document.getElementById('selection-status');

            if (masterSelect && statusSelect && previewBtn) {{
                const masterSelected = masterSelect.value;
                const statusSelected = statusSelect.value;

                if (masterSelected && statusSelected && masterSelected !== statusSelected) {{
                    previewBtn.disabled = false;
                    previewBtn.className = 'bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-all duration-200 transform hover:scale-105';
                    if (selectionStatus) selectionStatus.classList.remove('hidden');
                }} else {{
                    previewBtn.disabled = true;
                    previewBtn.className = 'bg-gray-400 text-white px-6 py-3 rounded-md font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
                    if (selectionStatus) selectionStatus.classList.add('hidden');
                }}
            }}
        }}

        // Preview sheets
        function previewSheets() {{
            const masterSheet = document.getElementById('master-sheet').value;
            const statusSheet = document.getElementById('status-sheet').value;

            if (masterSheet && statusSheet && currentFileId) {{
                // Store selections
                localStorage.setItem('selectedMasterSheet', masterSheet);
                localStorage.setItem('selectedStatusSheet', statusSheet);
                
                // Move to next step
                moveToStep(3);
                // In a real implementation, this would load preview data
            }}
        }}

        // Run transform
        async function runTransform() {{
            const transformBtn = document.getElementById('run-transform-btn');
            const transformProgress = document.getElementById('transform-progress');
            const progressBar = document.getElementById('transform-progress-bar');
            const statusText = document.getElementById('transform-status');
            const percentageText = document.getElementById('transform-percentage');

            const masterSheet = localStorage.getItem('selectedMasterSheet');
            const statusSheet = localStorage.getItem('selectedStatusSheet');

            if (!currentFileId || !masterSheet || !statusSheet) {{
                alert('Missing file or sheet information. Please start over.');
                return;
            }}

            // Disable button and show progress
            transformBtn.disabled = true;
            transformBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            transformProgress.classList.remove('hidden');

            try {{
                const transformData = {{
                    file_id: currentFileId,
                    master_sheet: masterSheet,
                    status_sheet: statusSheet
                }};

                const response = await fetch(`${{API_BASE_URL}}/api/transform`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(transformData)
                }});

                if (response.ok) {{
                    const result = await response.json();
                    
                    // Simulate progress
                    for (let i = 0; i <= 100; i += 10) {{
                        progressBar.style.width = i + '%';
                        percentageText.textContent = i + '%';
                        statusText.textContent = i < 100 ? 'Processing data...' : 'Transform complete!';
                        await new Promise(resolve => setTimeout(resolve, 300));
                    }}

                    // Show success
                    alert('Transform completed successfully! Check the results.');
                }} else {{
                    throw new Error('Transform failed');
                }}
            }} catch (error) {{
                console.error('Transform error:', error);
                statusText.textContent = 'Transform failed. Please try again.';
                statusText.className = 'text-sm text-red-600';
            }} finally {{
                transformBtn.disabled = false;
                transformBtn.innerHTML = '<i class="fas fa-play mr-2"></i>Run ETL Transform';
            }}
        }}

        // Reset steps
        function resetSteps() {{
            currentStep = 1;
            currentFileId = null;
            uploadedSheets = [];
            moveToStep(1);
            updateStepProgress(1, 0);
        }}

        // Health check on page load
        fetch(API_BASE_URL + '/api/health')
            .then(response => response.json())
            .then(data => {{
                console.log('API Health:', data);
            }})
            .catch(error => {{
                console.error('API Health Check Failed:', error);
            }});
    </script>
</body>
</html>
        """
        
        self.wfile.write(html_content.encode())
        return