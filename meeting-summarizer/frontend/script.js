const API_BASE = 'http://localhost:8000';

// Global variables
let currentMeetingData = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Meeting Summarizer loaded');
    
    const fileInput = document.getElementById('fileInput');
    const attachBtn = document.getElementById('attachBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const messagesContainer = document.getElementById('messages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');

    // Attach button click
    attachBtn.addEventListener('click', function() {
        fileInput.click();
    });

    // File selection handler
    fileInput.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        console.log('📁 File selected:', file.name);
        showMessage(`Uploaded audio file: ${file.name}`, 'user');
        
        // Show loading
        loadingOverlay.classList.add('show');
        loadingText.textContent = 'Processing your meeting audio...';

        try {
            const formData = new FormData();
            formData.append('audio', file);

            console.log('🔄 Sending to backend...');
            const response = await fetch(`${API_BASE}/meeting/summarize`, {
                method: 'POST',
                body: formData
            });

            console.log('📥 Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log('✅ Success! Displaying results...');
            
            // Store meeting data for chat
            currentMeetingData = result;
            
            loadingOverlay.classList.remove('show');
            displayResults(result);
            
            // Enable chat input
            enableChat();

        } catch (error) {
            console.error('❌ Error:', error);
            loadingOverlay.classList.remove('show');
            showMessage(`Error: ${error.message}`, 'ai');
        }
    });

    // Send button for chat
    sendBtn.addEventListener('click', handleChatMessage);
    
    // Enter key for chat input
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleChatMessage();
        }
    });

    async function handleChatMessage() {
        const message = chatInput.value.trim();
        if (!message || !currentMeetingData) return;

        // Show user message
        showMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        const thinkingMsg = showMessage('Thinking...', 'ai');
        thinkingMsg.classList.add('thinking');

        try {
            // Send chat message to your backend
            const response = await fetch(`${API_BASE}/meeting/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    meeting_id: currentMeetingData.id,
                    question: message,
                    transcript: currentMeetingData.transcript_preview,
                    summary: currentMeetingData.summary
                })
            });

            if (!response.ok) {
                throw new Error(`Chat error: ${response.status}`);
            }

            const chatResult = await response.json();
            
            // Remove thinking message
            thinkingMsg.remove();
            
            // Show AI response
            showMessage(chatResult.answer, 'ai');

        } catch (error) {
            console.error('❌ Chat error:', error);
            thinkingMsg.remove();
            showMessage(`Error: ${error.message}`, 'ai');
        }
    }

    function enableChat() {
        chatInput.disabled = false;
        chatInput.placeholder = "Ask a question about this meeting...";
        sendBtn.disabled = false;
        
        showMessage('You can now ask questions about this meeting! What would you like to know?', 'ai');
    }

    function displayResults(data) {
        console.log('📊 Data received:', data);
        
        if (data && data.summary) {
            const summary = data.summary;
            
            // Show main summary
            if (summary.summary) {
                showMessage(`
                    <h3>📋 Meeting Summary</h3>
                    <p>${summary.summary}</p>
                `, 'ai');
            }
            
            // Show decisions
            if (summary.key_decisions && summary.key_decisions.length > 0) {
                const decisionsHTML = summary.key_decisions.map(d => `<li>${d}</li>`).join('');
                showMessage(`
                    <h3>✅ Key Decisions</h3>
                    <ul>${decisionsHTML}</ul>
                `, 'ai');
            }
            
            // Show action items
            if (summary.action_items && summary.action_items.length > 0) {
                const actionsHTML = summary.action_items.map(item => `
                    <div class="action-item">
                        <strong>${item.task}</strong><br>
                        <small>👤 ${item.assignee || 'Unassigned'} ${item.deadline ? `• 📅 ${item.deadline}` : ''}</small>
                    </div>
                `).join('');
                showMessage(`
                    <h3>🎯 Action Items</h3>
                    ${actionsHTML}
                `, 'ai');
            }
        }
    }

    function showMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return messageDiv;
    }

    // Welcome message
    showMessage('Hello! Upload a meeting audio file to get started. I\'ll transcribe it and provide a summary with key decisions and action items.', 'ai');
});