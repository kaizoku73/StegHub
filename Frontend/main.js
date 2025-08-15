// Enhanced Steghub Frontend JavaScript with Better CORS and Error Handling

class SteghubApp {
    constructor() {
        this.POSSIBLE_API_URLS = [
            'http://localhost:8000',
            'http://127.0.0.1:8000',
            'http://0.0.0.0:8000'
        ];
        this.API_BASE_URL = null;
        this.currentMode = 'image';
        this.connectionTested = false;
        this.init();
    }

    async init() {
        console.log('Initializing SteghubApp...');
        
        // Test backend connection first
        await this.establishConnection();
        
        // Setup UI
        this.setupEventListeners();
        this.setupCharCounters();
        this.showSection('imageSection');
        this.hideSection('audioSection');
        
        console.log('SteghubApp initialized successfully');
    }

    async establishConnection() {
        console.log('Testing backend connections...');
        
        for (const url of this.POSSIBLE_API_URLS) {
            try {
                console.log(`Testing connection to: ${url}`);
                
                const response = await fetch(`${url}/`, {
                    method: 'GET'
                });
                
                if (response.ok) {
                    this.API_BASE_URL = url;
                    this.connectionTested = true;
                    console.log(`✅ Connected to backend at: ${url}`);
                    return true;
                }
            } catch (error) {
                console.log(`❌ Failed to connect to ${url}:`, error.message);
            }
        }
        
        console.error('❌ Could not connect to any backend URL');
        this.showResult('error', 'Cannot connect to backend server. Please make sure it is running on port 8000.');
        return false;
    }

    async makeAPIRequest(endpoint, formData) {
        const errors = [];
        
        for (const baseUrl of this.POSSIBLE_API_URLS) {
            try {
                console.log(`Making request to: ${baseUrl}${endpoint}`);
                
                const response = await fetch(`${baseUrl}${endpoint}`, {
                    method: 'POST',
                    body: formData,
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return response;
                
            } catch (error) {
                console.error(`❌ Request failed to ${baseUrl}:`, error);
                errors.push(`${baseUrl}: ${error.message}`);
            }
        }
        
        throw new Error(`Failed to connect to any backend URL:\n${errors.join('\n')}`);
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Main mode toggle
        const modeToggle = document.getElementById('modeToggle');
        if (modeToggle) {
            modeToggle.addEventListener('change', (e) => {
                console.log('Mode toggle changed:', e.target.checked);
                this.toggleMode(e.target.checked);
            });
        }

        // Operation toggles for each method
        this.setupOperationToggles();

        // Form submissions
        this.setupFormSubmissions();
    }

    toggleMode(isAudio) {
        console.log('Toggling mode to:', isAudio ? 'audio' : 'image');
        this.currentMode = isAudio ? 'audio' : 'image';
        
        const imageSection = document.getElementById('imageSection');
        const audioSection = document.getElementById('audioSection');
        
        if (isAudio) {
            if (imageSection) imageSection.classList.remove('active');
            if (audioSection) audioSection.classList.add('active');
        } else {
            if (audioSection) audioSection.classList.remove('active');
            if (imageSection) imageSection.classList.add('active');
        }
    }

    showSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('active');
            console.log('Showing section:', sectionId);
        }
    }

    hideSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('active');
            console.log('Hiding section:', sectionId);
        }
    }

    setupOperationToggles() {
        const toggleButtons = document.querySelectorAll('.toggle-btn');
        console.log('Found toggle buttons:', toggleButtons.length);
        
        toggleButtons.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const method = e.target.dataset.method;
                const operation = e.target.dataset.operation;
                console.log('Toggle clicked:', method, operation);
                this.switchOperation(method, operation, e.target);
            });
        });
    }

    switchOperation(method, operation, clickedButton) {
        console.log('Switching operation:', method, operation);
        
        const methodCard = clickedButton.closest('.method-card');
        if (!methodCard) {
            console.log('Method card not found');
            return;
        }
        
        // Update toggle buttons in this card
        const toggleButtons = methodCard.querySelectorAll('.toggle-btn');
        toggleButtons.forEach(btn => btn.classList.remove('active'));
        clickedButton.classList.add('active');
        
        // Show/hide forms in this card
        const forms = methodCard.querySelectorAll('.operation-form');
        forms.forEach(form => {
            form.classList.remove('active');
            if (form.id.includes(operation)) {
                form.classList.add('active');
                console.log('Activated form:', form.id);
            }
        });
    }

    setupCharCounters() {
        // Histogram message counter
        const histogramMessage = document.getElementById('histogram-embed-message');
        const histogramCounter = document.getElementById('histogram-embed-counter');
        
        if (histogramMessage && histogramCounter) {
            histogramMessage.addEventListener('input', (e) => {
                const count = e.target.value.length;
                histogramCounter.textContent = `${count}/100`;
                
                if (count > 90) {
                    histogramCounter.style.color = '#ff4444';
                } else if (count > 70) {
                    histogramCounter.style.color = '#ffc107';
                } else {
                    histogramCounter.style.color = '#00cc33';
                }
            });
        }

        // Phase message counter
        const phaseMessage = document.getElementById('phase-embed-message');
        const phaseCounter = document.getElementById('phase-embed-counter');
        
        if (phaseMessage && phaseCounter) {
            phaseMessage.addEventListener('input', (e) => {
                const count = e.target.value.length;
                phaseCounter.textContent = `${count}/100`;
                
                if (count > 90) {
                    phaseCounter.style.color = '#ff4444';
                } else if (count > 70) {
                    phaseCounter.style.color = '#ffc107';
                } else {
                    phaseCounter.style.color = '#00cc33';
                }
            });
        }
    }

    setupFormSubmissions() {
        console.log('Setting up form submissions...');
        
        // Image LSB forms
        this.setupFormHandler('lsb-image-embed', () => this.handleImageLSBEmbed());
        this.setupFormHandler('lsb-image-extract', () => this.handleImageLSBExtract());

        // Histogram forms
        this.setupFormHandler('histogram-embed', () => this.handleHistogramEmbed());
        this.setupFormHandler('histogram-extract', () => this.handleHistogramExtract());

        // Audio LSB forms
        this.setupFormHandler('lsb-audio-embed', () => this.handleAudioLSBEmbed());
        this.setupFormHandler('lsb-audio-extract', () => this.handleAudioLSBExtract());

        // Phase Coding forms
        this.setupFormHandler('phase-embed', () => this.handlePhaseEmbed());
        this.setupFormHandler('phase-extract', () => this.handlePhaseExtract());
    }

    setupFormHandler(formId, handler) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                console.log(`${formId} form submitted`);
                handler();
            });
        }
    }

    validateFormData(data) {
        for (const [key, value] of Object.entries(data)) {
            if (!value || (typeof value === 'string' && value.trim() === '')) {
                throw new Error(`${key.replace(/([A-Z])/g, ' $1').toLowerCase()} is required`);
            }
        }
    }

    // ==================== IMAGE LSB METHODS ====================

    async handleImageLSBEmbed() {
        console.log('Starting Image LSB Embed');
        this.showLoading();
        
        try {
            const coverImage = document.getElementById('lsb-image-embed-cover').files[0];
            const secretFile = document.getElementById('lsb-image-embed-secret').files[0];
            const key = document.getElementById('lsb-image-embed-password').value;
            
            this.validateFormData({ coverImage, secretFile, key });
            
            // Validate PNG format
            if (!coverImage.type.includes('png')) {
                throw new Error('Cover image must be in PNG format');
            }
            
            const formData = new FormData();
            formData.append('cover_image', coverImage);
            formData.append('secret_file', secretFile);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/embed/image/lsb', formData);
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'stego_image.png');
                this.showResult('success', 'File successfully embedded in image!');
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Image LSB Embed error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    async handleImageLSBExtract() {
        console.log('Starting Image LSB Extract');
        this.showLoading();
        
        try {
            const stegoImage = document.getElementById('lsb-image-extract-stego').files[0];
            const key = document.getElementById('lsb-image-extract-password').value;
            
            this.validateFormData({ stegoImage, key });
            
            const formData = new FormData();
            formData.append('stego_image', stegoImage);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/extract/image/lsb', formData);
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'extracted_file');
                this.showResult('success', 'File successfully extracted from image!');
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Image LSB Extract error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    // ==================== HISTOGRAM METHODS ====================

    async handleHistogramEmbed() {
        console.log('Starting Histogram Embed');
        this.showLoading();
        
        try {
            const coverImage = document.getElementById('histogram-embed-cover').files[0];
            const message = document.getElementById('histogram-embed-message').value;
            const key = document.getElementById('histogram-embed-key').value;
            
            this.validateFormData({ coverImage, message, key });
            
            if (message.length > 100) {
                throw new Error('Message too long. Maximum 100 characters allowed.');
            }
            
            const formData = new FormData();
            formData.append('cover_image', coverImage);
            formData.append('message', message);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/embed/image/histogram', formData);
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'histogram_stego.png');
                this.showResult('success', 'Message successfully embedded using histogram manipulation!');
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Histogram embed error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    async handleHistogramExtract() {
        console.log('Starting Histogram Extract');
        this.showLoading();
        
        try {
            const stegoImage = document.getElementById('histogram-extract-stego').files[0];
            const key = document.getElementById('histogram-extract-key').value;
            
            this.validateFormData({ stegoImage, key });
            
            const formData = new FormData();
            formData.append('stego_image', stegoImage);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/extract/image/histogram', formData);
            
            if (response.ok) {
                const result = await response.json();
                this.showResult('message', `Extracted message: ${result.message}`);
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Histogram extract error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    // ==================== AUDIO LSB METHODS ====================

    async handleAudioLSBEmbed() {
        console.log('Starting Audio LSB Embed');
        this.showLoading();
        
        try {
            const coverAudio = document.getElementById('lsb-audio-embed-cover').files[0];
            const secretFile = document.getElementById('lsb-audio-embed-secret').files[0];
            const key = document.getElementById('lsb-audio-embed-key').value;
            
            this.validateFormData({ coverAudio, secretFile, key });
            
            const formData = new FormData();
            formData.append('cover_audio', coverAudio);
            formData.append('secret_file', secretFile);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/embed/audio/lsb', formData);
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'stego_audio.wav');
                this.showResult('success', 'File successfully embedded in audio!');
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Audio LSB embed error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    async handleAudioLSBExtract() {
        console.log('Starting Audio LSB Extract');
        this.showLoading();
        
        try {
            const stegoAudio = document.getElementById('lsb-audio-extract-stego').files[0];
            const key = document.getElementById('lsb-audio-extract-key').value;
            
            this.validateFormData({ stegoAudio, key });
            
            const formData = new FormData();
            formData.append('stego_audio', stegoAudio);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/extract/audio/lsb', formData);
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'extracted_file');
                this.showResult('success', 'File successfully extracted from audio!');
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Audio LSB extract error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    // ==================== PHASE CODING METHODS ====================

    async handlePhaseEmbed() {
        console.log('Starting Phase Embed');
        this.showLoading();
        
        try {
            const coverAudio = document.getElementById('phase-embed-cover').files[0];
            const message = document.getElementById('phase-embed-message').value;
            const key = document.getElementById('phase-embed-key').value;
            
            this.validateFormData({ coverAudio, message, key });
            
            if (message.length > 100) {
                throw new Error('Message too long. Maximum 100 characters allowed.');
            }
            
            const formData = new FormData();
            formData.append('cover_audio', coverAudio);
            formData.append('message', message);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/embed/audio/phase', formData);
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'phase_stego.wav');
                this.showResult('success', 'Message successfully embedded using phase coding!');
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Phase embed error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    async handlePhaseExtract() {
        console.log('Starting Phase Extract');
        this.showLoading();
        
        try {
            const stegoAudio = document.getElementById('phase-extract-stego').files[0];
            const key = document.getElementById('phase-extract-key').value;
            
            this.validateFormData({ stegoAudio, key });
            
            const formData = new FormData();
            formData.append('stego_audio', stegoAudio);
            formData.append('key', key);
            
            const response = await this.makeAPIRequest('/extract/audio/phase', formData);
            
            if (response.ok) {
                const result = await response.json();
                this.showResult('message', `Extracted message: ${result.message}`);
            } else {
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message);
            }
        } catch (error) {
            console.error('Phase extract error:', error);
            this.showResult('error', error.message);
        } finally {
            this.hideLoading();
        }
    }

    // ==================== UTILITY METHODS ====================

    async parseErrorResponse(response) {
        try {
            const errorText = await response.text();
            const errorJson = JSON.parse(errorText);
            return {
                status: response.status,
                message: errorJson.detail || errorJson.message || `Request failed with status ${response.status}`
            };
        } catch (e) {
            return {
                status: response.status,
                message: `Request failed with status ${response.status}`
            };
        }
    }

    downloadFile(blob, filename) {
        try {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            console.log(`File downloaded: ${filename}`);
        } catch (error) {
            console.error('Download error:', error);
            this.showResult('error', 'Failed to download file');
        }
    }

    showResult(type, message) {
        const resultsSection = document.getElementById('resultsSection');
        const resultContent = document.getElementById('resultContent');
        
        if (resultsSection && resultContent) {
            resultsSection.classList.add('show');
            
            let cssClass = '';
            let icon = '';
            
            switch (type) {
                case 'success':
                    cssClass = 'result-success';
                    icon = '✅';
                    break;
                case 'message':
                    cssClass = 'result-message';
                    icon = '📄';
                    break;
                case 'error':
                    cssClass = 'result-error';
                    icon = '❌';
                    break;
                default:
                    cssClass = 'result-success';
                    icon = 'ℹ️';
            }
            
            resultContent.innerHTML = `<div class="${cssClass}">${icon} ${message}</div>`;
            
            // Scroll to results
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }

    showLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('show');
            console.log('Loading overlay shown');
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('show');
            console.log('Loading overlay hidden');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing SteghubApp');
    try {
        new SteghubApp();
    } catch (error) {
        console.error('Failed to initialize SteghubApp:', error);
        alert('Failed to initialize application. Please refresh the page.');
    }
});