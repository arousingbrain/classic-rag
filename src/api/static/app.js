const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const fileList = document.getElementById('file-list');
const rawTextInput = document.getElementById('raw-text-input');
const ingestTextBtn = document.getElementById('ingest-text-btn');
const clearDbBtn = document.getElementById('clear-db-btn');

// --- Chat Functionality ---

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to UI
    appendMessage('user', message);
    userInput.value = '';

    // Show loading state
    const loadingMsg = appendMessage('assistant', 'Thinking...', true);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        chatMessages.removeChild(loadingMsg);

        if (data.answer) {
            appendMessage('assistant', data.answer, false, data.sources);
        } else {
            appendMessage('assistant', 'Sorry, I encountered an error.');
        }
    } catch (error) {
        chatMessages.removeChild(loadingMsg);
        appendMessage('assistant', 'Error connecting to the server.');
    }
});

function appendMessage(role, text, isLoading = false, sources = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    let contentHtml = `<div class="message-content">${text}</div>`;
    
    if (sources && sources.length > 0) {
        const sourceTags = sources.map(s => `<span class="source-tag">${s.id}</span>`).join(' ');
        contentHtml += `<div class="sources">Sources: ${sourceTags}</div>`;
    }

    msgDiv.innerHTML = contentHtml;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv;
}

// --- File Upload Functionality ---

uploadBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

async function handleFiles(files) {
    for (const file of files) {
        addFileToList(file.name, 'uploading');
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            updateFileStatus(file.name, 'success');
        } catch (error) {
            updateFileStatus(file.name, 'error');
        }
    }
}

// --- Raw Text Ingestion ---

ingestTextBtn.addEventListener('click', async () => {
    const text = rawTextInput.value.trim();
    if (!text) return;

    const timestamp = new Date().toLocaleTimeString();
    const virtualName = `Input @ ${timestamp}`;
    
    addFileToList(virtualName, 'ingesting');
    ingestTextBtn.disabled = true;
    ingestTextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ingesting...';

    try {
        const response = await fetch('/ingest-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text,
                filename: `manual_input_${Date.now()}.txt`
            })
        });

        const data = await response.json();
        updateFileStatus(virtualName, 'success');
        rawTextInput.value = '';
    } catch (error) {
        updateFileStatus(virtualName, 'error');
    } finally {
        ingestTextBtn.disabled = false;
        ingestTextBtn.innerHTML = '<i class="fas fa-file-import"></i> Ingest Text';
    }
});

function addFileToList(name, status) {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.id = `file-${name}`;
    item.innerHTML = `
        <i class="far fa-file-alt"></i>
        <span class="file-name">${name}</span>
        <span class="file-status ${status}">${status}</span>
    `;
    fileList.prepend(item);
}

function updateFileStatus(name, status) {
    const item = document.getElementById(`file-${name}`);
    if (item) {
        const statusSpan = item.querySelector('.file-status');
        statusSpan.className = `file-status ${status}`;
        statusSpan.textContent = status;
    }
}

// --- Database Actions ---

clearDbBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to clear the entire knowledge base? This action cannot be undone.')) return;

    try {
        const response = await fetch('/documents/clear', { method: 'POST' });
        const data = await response.json();
        alert('Knowledge base cleared successfully.');
        fileList.innerHTML = '';
    } catch (error) {
        alert('Error clearing the database.');
    }
});
