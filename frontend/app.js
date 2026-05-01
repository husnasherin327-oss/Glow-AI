// Global state
let state = {
    apiKey: '',
    conversationHistory: [],
    skinProfile: {}
};

const API_URL = 'http://localhost:8000/chat/';

// Helper to safely get DOM elements inside functions
function getDOM() {
    return {
        modal: document.getElementById('apiKeyModal'),
        apiKeyInput: document.getElementById('apiKeyInput'),
        saveApiBtn: document.getElementById('saveApiKeyBtn'),
        skipApiBtn: document.getElementById('skipApiKeyBtn'),
        chatHistory: document.getElementById('chatHistory'),
        userInput: document.getElementById('userInput'),
        sendBtn: document.getElementById('sendBtn'),
        resetBtn: document.getElementById('resetBtn'),
        typingIndicator: document.getElementById('typingIndicator'),
        profileEmpty: document.getElementById('profileEmptyState'),
        profileContent: document.getElementById('profileContent'),
    };
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    const DOM = getDOM();

    // Check if any critical elements are missing
    if (!DOM.sendBtn || !DOM.userInput || !DOM.chatHistory) {
        console.error("Critical DOM elements missing!", DOM);
        return;
    }

    // Check if key saved in session
    const savedKey = sessionStorage.getItem('hf_token');
    if (savedKey) {
        state.apiKey = savedKey;
        if (DOM.modal) DOM.modal.classList.remove('active');
    }

    // Attach listeners
    if (DOM.saveApiBtn) {
        DOM.saveApiBtn.addEventListener('click', () => {
            const key = DOM.apiKeyInput.value.trim();
            if (key) {
                state.apiKey = key;
                sessionStorage.setItem('hf_token', key);
            }
            DOM.modal.classList.remove('active');
        });
    }

    if (DOM.skipApiBtn) {
        DOM.skipApiBtn.addEventListener('click', () => {
            DOM.modal.classList.remove('active');
        });
    }

    DOM.sendBtn.addEventListener('click', () => {
        console.log("Send button clicked");
        handleSend();
    });

    DOM.userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            console.log("Enter key pressed");
            handleSend();
        }
    });

    if (DOM.resetBtn) {
        DOM.resetBtn.addEventListener('click', () => {
            state.conversationHistory = [];
            state.skinProfile = {};
            DOM.chatHistory.innerHTML = `
                <div class="message assistant">
                    <div class="message-content">
                        Conversation reset. How can I help you regarding your skin today?
                    </div>
                </div>
                <div class="typing-indicator" id="typingIndicator">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                </div>
            `;
            updateProfileUI();
        });
    }
});

async function handleSend() {
    const DOM = getDOM();
    const message = DOM.userInput.value.trim();
    if (!message) return;

    console.log("Handling send for message:", message);

    try {
        // 1. Add User Message to UI & State
        appendMessage('user', message);
        DOM.userInput.value = '';
        
        // 2. Show Typing Indicator
        if (DOM.typingIndicator) {
            DOM.typingIndicator.classList.add('active');
        }
        DOM.chatHistory.scrollTop = DOM.chatHistory.scrollHeight;

        // 3. Call API
        const payload = {
            message: message,
            conversation_history: state.conversationHistory,
            skin_profile: state.skinProfile,
            api_key: state.apiKey || undefined
        };

        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'API request failed');
        }

        const data = await res.json();
        
        // 4. Update State
        state.conversationHistory.push({ role: 'user', content: message });
        state.conversationHistory.push({ role: 'assistant', content: data.message });
        if (data.skin_profile) {
            state.skinProfile = data.skin_profile;
            updateProfileUI();
        }

        // 5. Hide Typing Indicator
        if (DOM.typingIndicator) {
            DOM.typingIndicator.classList.remove('active');
        }

        // 6. Handle Response Types
        if (data.type === 'products' && data.products && data.products.length > 0) {
            appendProductRecommendation(data.message, data.skin_analysis, data.products);
        } else {
            appendMessage('assistant', data.message);
        }

    } catch (error) {
        console.error("Error in handleSend:", error);
        if (DOM.typingIndicator) {
            DOM.typingIndicator.classList.remove('active');
        }
        appendMessage('assistant', `<span style="color: #f43f5e;">Error: ${error.message}</span>`);
    }
}

// --- UI Helpers ---

function appendMessage(role, contentHTML) {
    const DOM = getDOM();
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const formatted = contentHTML.replace(/\n/g, '<br>');
    div.innerHTML = `<div class="message-content">${formatted}</div>`;
    
    if (DOM.typingIndicator) {
        DOM.chatHistory.insertBefore(div, DOM.typingIndicator);
    } else {
        DOM.chatHistory.appendChild(div);
    }
    DOM.chatHistory.scrollTop = DOM.chatHistory.scrollHeight;
}

function appendProductRecommendation(introMessage, analysis, products) {
    const DOM = getDOM();
    const wrapper = document.createElement('div');
    wrapper.className = `message assistant w-full max-w-full`;
    
    let html = `<div class="message-content" style="max-width: 100%; border-radius: 16px;">`;
    html += `<p style="margin-bottom: 20px">${introMessage.replace(/\n/g, '<br>')}</p>`;

    if (analysis && analysis.profile_summary) {
        html += `
        <div class="skin-analysis-box">
            <h4><i class="fa-solid fa-microscope"></i> AI Skin Analysis</h4>
            <p>${analysis.profile_summary}</p>
        </div>
        `;
    }

    html += `<div class="product-carousel">`;
    products.forEach(p => {
        html += `
        <div class="product-card">
            <div class="prod-brand">${p.brand || ''}</div>
            <div class="prod-name">${p.name || ''}</div>
        </div>
        `;
    });
    html += `</div></div>`;
    
    wrapper.innerHTML = html;
    if (DOM.typingIndicator) {
        DOM.chatHistory.insertBefore(wrapper, DOM.typingIndicator);
    } else {
        DOM.chatHistory.appendChild(wrapper);
    }
    DOM.chatHistory.scrollTop = DOM.chatHistory.scrollHeight;
}

function updateProfileUI() {
    const DOM = getDOM();
    const prof = state.skinProfile;
    if (!prof || Object.keys(prof).length === 0) return;

    if (DOM.profileEmpty) DOM.profileEmpty.style.display = 'none';
    if (DOM.profileContent) DOM.profileContent.classList.remove('hidden');

    const renderGroup = (id, dataOrArray) => {
        const container = document.getElementById(`${id}-container`);
        const group = document.getElementById(id);
        if (!group || !container) return;
        
        group.innerHTML = '';
        let data = Array.isArray(dataOrArray) ? dataOrArray : (dataOrArray ? [dataOrArray] : []);
        if (data.length > 0) {
            container.style.display = 'block';
            data.forEach(item => { if(item) group.innerHTML += `<span class="tag">${item}</span>`; });
        } else {
            container.style.display = 'none';
        }
    };

    renderGroup('prof-type', prof.skin_type);
    renderGroup('prof-conditions', prof.conditions);
    renderGroup('prof-concerns', prof.concerns);
}
