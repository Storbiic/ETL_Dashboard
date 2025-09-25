"""Simple test version for debugging styling."""
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve a simple test page."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETL Dashboard - Styling Test</title>
    
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Font Awesome CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        .test-animation {
            transition: all 0.3s ease;
        }
        .test-animation:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body class="bg-gradient-to-r from-blue-50 to-purple-50 min-h-screen">
    <div class="container mx-auto p-8">
        <div class="max-w-4xl mx-auto">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-4xl font-bold text-gray-800 mb-4">
                    <i class="fas fa-database text-blue-600 mr-3"></i>
                    ETL Dashboard - Styling Test
                </h1>
                <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                    <div class="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full" style="width: 100%"></div>
                </div>
                <p class="text-lg text-gray-600">If you can see colors, gradients, and styling, then CSS is working!</p>
            </div>

            <!-- Test Cards -->
            <div class="grid md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white rounded-xl shadow-lg p-6 test-animation border border-blue-100">
                    <div class="text-blue-600 mb-4">
                        <i class="fas fa-check-circle text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">Tailwind Working</h3>
                    <p class="text-gray-600">This card should be white with blue accents and shadow</p>
                </div>

                <div class="bg-gradient-to-br from-green-400 to-blue-500 rounded-xl shadow-lg p-6 text-white test-animation">
                    <div class="mb-4">
                        <i class="fas fa-paint-brush text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Custom CSS Working</h3>
                    <p class="text-green-100">This card should have a gradient background</p>
                </div>

                <div class="bg-white rounded-xl shadow-lg p-6 test-animation border-2 border-purple-200">
                    <div class="text-purple-600 mb-4">
                        <i class="fas fa-magic text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">Hover Effects</h3>
                    <p class="text-gray-600">Hover over this card to see animations</p>
                </div>
            </div>

            <!-- Upload Area Test -->
            <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
                <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">
                    <i class="fas fa-upload text-blue-600 mr-2"></i>
                    Upload Area Test
                </h2>
                <div class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 hover:bg-blue-50 transition-all duration-300">
                    <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                    <p class="text-lg font-medium text-gray-700 mb-2">Test Upload Area</p>
                    <p class="text-gray-500">Hover to see styling changes</p>
                </div>
            </div>

            <!-- Status Test -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Styling Status Check</h2>
                <div class="space-y-3">
                    <div class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        <span class="text-gray-700">HTML Structure: Working</span>
                    </div>
                    <div class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        <span class="text-gray-700">Font Awesome Icons: Working</span>
                    </div>
                    <div class="flex items-center">
                        <i class="fas fa-question text-yellow-500 mr-3"></i>
                        <span class="text-gray-700">Tailwind CSS: <span id="tailwind-status">Testing...</span></span>
                    </div>
                    <div class="flex items-center">
                        <i class="fas fa-question text-yellow-500 mr-3"></i>
                        <span class="text-gray-700">Custom CSS: <span id="custom-status">Testing...</span></span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Test if Tailwind is working
            const testDiv = document.createElement('div');
            testDiv.className = 'bg-red-500';
            document.body.appendChild(testDiv);
            
            const computedStyle = window.getComputedStyle(testDiv);
            const backgroundColor = computedStyle.backgroundColor;
            
            document.body.removeChild(testDiv);
            
            if (backgroundColor.includes('rgb(239, 68, 68)') || backgroundColor.includes('rgb(220, 38, 38)')) {
                document.getElementById('tailwind-status').textContent = '✅ Working';
                document.getElementById('tailwind-status').className = 'text-green-600 font-semibold';
            } else {
                document.getElementById('tailwind-status').textContent = '❌ Not Working';
                document.getElementById('tailwind-status').className = 'text-red-600 font-semibold';
            }
            
            // Test if custom CSS is working
            const testElement = document.querySelector('.test-animation');
            const transition = window.getComputedStyle(testElement).transition;
            
            if (transition && transition.includes('all')) {
                document.getElementById('custom-status').textContent = '✅ Working';
                document.getElementById('custom-status').className = 'text-green-600 font-semibold';
            } else {
                document.getElementById('custom-status').textContent = '❌ Not Working';
                document.getElementById('custom-status').className = 'text-red-600 font-semibold';
            }
            
            console.log('Styling test completed');
        });
    </script>
</body>
</html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))
        return