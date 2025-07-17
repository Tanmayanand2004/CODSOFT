/**
 * Kai - Ultra Minimalist Chat Interface
 */

class KaiChat {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messages = document.getElementById('messages');
        this.typing = document.getElementById('typing');
        this.themeToggle = document.getElementById('themeToggle');
        this.clearChat = document.getElementById('clearChat');
        this.quickBtns = document.querySelectorAll('.quick-btn');
        
        // Debug: Check if elements exist
        console.log('Elements found:', {
            messageInput: !!this.messageInput,
            sendBtn: !!this.sendBtn,
            messages: !!this.messages,
            typing: !!this.typing,
            themeToggle: !!this.themeToggle,
            clearChat: !!this.clearChat,
            quickBtns: this.quickBtns.length
        });
        
        this.isTyping = false;
        this.isDark = localStorage.getItem('kai-theme') === 'dark';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadTheme();
        this.messageInput.focus();
    }
    
    bindEvents() {
        // Send message events
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            this.messageInput.addEventListener('input', () => this.autoResize());
        }
        
        // Theme toggle
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => {
                console.log('Theme toggle clicked');
                this.toggleTheme();
            });
        }
        
        // Clear chat
        if (this.clearChat) {
            this.clearChat.addEventListener('click', () => this.clearMessages());
        }
        
        // Quick actions
        this.quickBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-msg');
                if (this.messageInput) {
                    this.messageInput.value = message;
                    this.sendMessage();
                }
            });
        });
    }
    
    autoResize() {
        if (this.messageInput) {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        }
    }
    
    async sendMessage() {
        console.log('Send message called');
        const message = this.messageInput.value.trim();
        console.log('Message:', message, 'IsTyping:', this.isTyping);
        
        if (!message || this.isTyping) {
            console.log('Message blocked - empty or typing');
            return;
        }
        
        console.log('Adding user message...');
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResize();
        this.showTyping();
        
        try {
            console.log('Sending to backend...');
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            setTimeout(() => {
                this.hideTyping();
                this.addMessage(data.response, 'bot');
            }, 800);
            
        } catch (error) {
            console.error('Send message error:', error);
            this.hideTyping();
            this.addMessage('Sorry, connection error. Please try again.', 'bot');
        }
    }
    
    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        this.messages.appendChild(messageDiv);
        this.messages.scrollTop = this.messages.scrollHeight;
    }
    
    showTyping() {
        this.isTyping = true;
        if (this.typing) {
            this.typing.innerHTML = `
                <span class="typing-text">Kai is thinking</span>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            this.typing.style.display = 'flex';
        }
        if (this.sendBtn) {
            this.sendBtn.disabled = true;
        }
        if (this.messages) {
            this.messages.scrollTop = this.messages.scrollHeight;
        }
    }
    
    hideTyping() {
        this.isTyping = false;
        if (this.typing) {
            this.typing.style.display = 'none';
        }
        if (this.sendBtn) {
            this.sendBtn.disabled = false;
        }
    }
    
    toggleTheme() {
        console.log('Toggle theme called, current isDark:', this.isDark);
        this.isDark = !this.isDark;
        console.log('New isDark value:', this.isDark);
        this.loadTheme();
        localStorage.setItem('kai-theme', this.isDark ? 'dark' : 'light');
        console.log('Theme saved to localStorage:', localStorage.getItem('kai-theme'));
    }
    
    loadTheme() {
        if (this.isDark) {
            document.body.classList.add('dark');
            this.themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            document.body.classList.remove('dark');
            this.themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }
    
    clearMessages() {
        const messages = this.messages.querySelectorAll('.message');
        messages.forEach(msg => msg.remove());
        
        const welcome = document.createElement('div');
        welcome.className = 'welcome';
        welcome.innerHTML = '<h3>👋 Hello!</h3><p>I\'m Kai, your AI assistant. How can I help you today?</p>';
        this.messages.appendChild(welcome);
    }
}

document.addEventListener('DOMContentLoaded', () => new KaiChat());
