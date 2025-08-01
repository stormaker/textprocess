class TextProcessor {
    constructor() {
        this.settings = this.loadSettings();
        this.initializeElements();
        this.bindEvents();
        this.applyTheme();
        this.setDefaultPrompt();
    }

    initializeElements() {
        this.inputText = document.getElementById('inputText');
        this.promptText = document.getElementById('promptText');
        this.processBtn = document.getElementById('processBtn');
        this.outputText = document.getElementById('outputText');
        this.outputActions = document.getElementById('outputActions');
        this.copyBtn = document.getElementById('copyBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        
        // Settings modal elements
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeModal = document.getElementById('closeModal');
        this.apiKeyInput = document.getElementById('apiKey');
        this.baseUrlInput = document.getElementById('baseUrl');
        this.modelInput = document.getElementById('model');
        this.maxWorkersInput = document.getElementById('maxWorkers');
        this.darkModeToggle = document.getElementById('darkMode');
        this.saveSettingsBtn = document.getElementById('saveSettings');
    }

    bindEvents() {
        this.processBtn.addEventListener('click', () => this.processText());
        this.copyBtn.addEventListener('click', () => this.copyResult());
        this.downloadBtn.addEventListener('click', () => this.downloadResult());
        
        // Settings modal events
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeModal.addEventListener('click', () => this.closeSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.darkModeToggle.addEventListener('change', () => this.toggleTheme());
        
        // Close modal when clicking outside
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });

        // Auto-resize textareas
        this.inputText.addEventListener('input', () => this.autoResize(this.inputText));
        this.promptText.addEventListener('input', () => this.autoResize(this.promptText));
    }

    setDefaultPrompt() {
        const defaultPrompt = `你是会议记录整理人员，以下是一段录音的逐字稿，请逐字将其整理成前后连贯的文字，需要注意：
1.保留完整保留原始录音的所有细节。
2.尽量保留原文语义、语感
3.请修改错别字，符合中文语法规范。
4.去掉说话人和时间戳。
5.采用第一人称：我。
6.请足够详细，字数越多越好。
7.保持原始录音逐字稿的语言风格。
8.直接输出结果，不要添加其他提示。`;
        
        this.promptText.value = defaultPrompt;
    }

    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    loadSettings() {
        const defaultSettings = {
            apiKey: '',
            baseUrl: 'https://api.openai.com/v1',
            model: 'gpt-4o',
            maxWorkers: 5,
            darkMode: false
        };
        
        const saved = localStorage.getItem('textProcessorSettings');
        return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
    }

    saveSettingsToStorage() {
        localStorage.setItem('textProcessorSettings', JSON.stringify(this.settings));
    }

    openSettings() {
        this.apiKeyInput.value = this.settings.apiKey;
        this.baseUrlInput.value = this.settings.baseUrl;
        this.modelInput.value = this.settings.model;
        this.maxWorkersInput.value = this.settings.maxWorkers;
        this.darkModeToggle.checked = this.settings.darkMode;
        this.settingsModal.style.display = 'block';
    }

    closeSettings() {
        this.settingsModal.style.display = 'none';
    }

    saveSettings() {
        this.settings.apiKey = this.apiKeyInput.value;
        this.settings.baseUrl = this.baseUrlInput.value;
        this.settings.model = this.modelInput.value.trim() || 'gpt-4o';
        this.settings.maxWorkers = Math.max(1, Math.min(10, parseInt(this.maxWorkersInput.value) || 5));
        this.settings.darkMode = this.darkModeToggle.checked;
        
        this.saveSettingsToStorage();
        this.applyTheme();
        this.closeSettings();
        
        this.showNotification('Settings saved successfully!', 'success');
    }

    toggleTheme() {
        this.settings.darkMode = this.darkModeToggle.checked;
        this.applyTheme();
    }

    applyTheme() {
        if (this.settings.darkMode) {
            document.body.setAttribute('data-theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1001;
            animation: slideIn 0.3s ease;
        `;
        
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ffc107';
                notification.style.color = '#333';
                break;
            default:
                notification.style.backgroundColor = '#17a2b8';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    async testConnection() {
        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: this.settings.apiKey,
                base_url: this.settings.baseUrl
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Connection failed');
        }

        const data = await response.json();
        return data;
    }

    async startProcessing(text, prompt) {
        const sessionId = Date.now().toString();
        
        const response = await fetch('/api/process-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                prompt: prompt,
                api_key: this.settings.apiKey,
                base_url: this.settings.baseUrl,
                model: this.settings.model,
                max_workers: this.settings.maxWorkers,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Processing failed to start');
        }

        const data = await response.json();
        return sessionId;
    }

    async checkProcessingStatus(sessionId) {
        const response = await fetch(`/api/processing-status/${sessionId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get status');
        }
        
        const data = await response.json();
        return data;
    }

    updateProgress(current, total) {
        const percentage = Math.round((current / total) * 100);
        this.progressFill.style.width = `${percentage}%`;
        this.progressText.textContent = `${percentage}% (${current}/${total})`;
    }

    async processText() {
        const inputText = this.inputText.value.trim();
        const prompt = this.promptText.value.trim();

        if (!inputText) {
            this.showNotification('Please enter some text to process', 'warning');
            return;
        }

        if (!prompt) {
            this.showNotification('Please enter a processing prompt', 'warning');
            return;
        }

        if (!this.settings.apiKey) {
            this.showNotification('Please set your OpenAI API key in settings', 'error');
            this.openSettings();
            return;
        }

        try {
            this.processBtn.disabled = true;
            this.processBtn.textContent = 'Processing...';
            this.progressSection.style.display = 'block';
            this.outputText.textContent = '';
            this.outputActions.style.display = 'none';

            // Test connection first
            await this.testConnection();
            this.showNotification('Connection successful, starting processing...', 'info');

            // Start processing
            const sessionId = await this.startProcessing(inputText, prompt);
            
            // Poll for status updates
            const pollInterval = setInterval(async () => {
                try {
                    const status = await this.checkProcessingStatus(sessionId);
                    
                    this.updateProgress(status.completed_chunks, status.total_chunks);
                    
                    if (status.status === 'completed') {
                        clearInterval(pollInterval);
                        this.outputText.textContent = status.results;
                        this.outputActions.style.display = 'flex';
                        this.showNotification('Text processing completed successfully!', 'success');
                        
                        this.processBtn.disabled = false;
                        this.processBtn.textContent = 'Process Text';
                        this.progressSection.style.display = 'none';
                        
                    } else if (status.status === 'error') {
                        clearInterval(pollInterval);
                        throw new Error(status.error || 'Processing failed');
                    }
                    
                } catch (error) {
                    clearInterval(pollInterval);
                    throw error;
                }
            }, 1000); // Poll every second

        } catch (error) {
            console.error('Processing error:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
            this.outputText.textContent = `Error occurred during processing: ${error.message}`;
            
            this.processBtn.disabled = false;
            this.processBtn.textContent = 'Process Text';
            this.progressSection.style.display = 'none';
        }
    }

    async copyResult() {
        const content = this.outputText.textContent;
        if (!content) {
            this.showNotification('No content to copy', 'warning');
            return;
        }

        try {
            await navigator.clipboard.writeText(content);
            this.showNotification('Text copied to clipboard!', 'success');
            
            // Visual feedback - temporarily change button text
            const originalText = this.copyBtn.textContent;
            this.copyBtn.textContent = '✅ Copied!';
            this.copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                this.copyBtn.textContent = originalText;
                this.copyBtn.style.background = '';
            }, 2000);
            
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = content;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showNotification('Text copied to clipboard!', 'success');
            } catch (err) {
                this.showNotification('Failed to copy text. Please copy manually.', 'error');
            }
            
            document.body.removeChild(textArea);
        }
    }

    downloadResult() {
        const content = this.outputText.textContent;
        if (!content) {
            this.showNotification('No content to download', 'warning');
            return;
        }

        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `processed_text_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('File downloaded successfully!', 'success');
    }
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new TextProcessor();
});