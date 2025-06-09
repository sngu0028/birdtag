// Mock data for testing without backend
const MOCK_DATA = {
    uploadedFiles: [],
    searchResults: [
        {
            id: 1,
            url: 'https://via.placeholder.com/300x200?text=Crow+Image',
            thumbnail: 'https://via.placeholder.com/150x100?text=Crow+Thumb',
            tags: ['crow', 'blackbird'],
            type: 'image'
        },
        {
            id: 2,
            url: 'https://via.placeholder.com/300x200?text=Sparrow+Image',
            thumbnail: 'https://via.placeholder.com/150x100?text=Sparrow+Thumb',
            tags: ['sparrow'],
            type: 'image'
        },
        {
            id: 3,
            url: 'https://via.placeholder.com/300x200?text=Eagle+Image',
            thumbnail: 'https://via.placeholder.com/150x100?text=Eagle+Thumb',
            tags: ['eagle', 'hawk'],
            type: 'image'
        }
    ],
    userSubscriptions: ['crow', 'eagle']
};

// Navigation handling
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (e.target.id === 'signOutBtn') {
            if (confirm('Are you sure you want to sign out?')) {
                alert('Sign out functionality will be connected to Cognito');
                return;
            }
        }
        
        const section = e.target.dataset.section;
        if (section) {
            // Update active nav button
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Show corresponding section
            document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
            document.getElementById(`${section}Section`).classList.add('active');
        }
    });
});

// File Upload Functionality
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const uploadBtn = document.getElementById('uploadBtn');
const filePreview = document.getElementById('filePreview');
const browseBtn = document.querySelector('.browse-btn');

// Click to browse files
browseBtn.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('click', () => fileInput.click());

// Drag and drop
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

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    filePreview.innerHTML = '';
    uploadBtn.disabled = files.length === 0;
    
    Array.from(files).forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                fileItem.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}">
                    <div class="file-info">${file.name}</div>
                    <button class="remove-btn" onclick="removeFile(this)">×</button>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            fileItem.innerHTML = `
                <div style="padding: 50px; text-align: center; background: #f0f0f0;">
                    <div>${file.type.includes('audio') ? '🎵' : '🎥'}</div>
                    <div class="file-info">${file.name}</div>
                </div>
                <button class="remove-btn" onclick="removeFile(this)">×</button>
            `;
        }
        
        filePreview.appendChild(fileItem);
        MOCK_DATA.uploadedFiles.push(file);
    });
}

function removeFile(btn) {
    btn.parentElement.remove();
    // Update upload button state
    uploadBtn.disabled = filePreview.children.length === 0;
}

// Upload button click
uploadBtn.addEventListener('click', async () => {
    const progressContainer = document.getElementById('uploadProgress');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    
    progressContainer.style.display = 'block';
    uploadBtn.disabled = true;
    
    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
        
        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                alert('Files uploaded successfully! (Mock upload - backend integration needed)');
                progressContainer.style.display = 'none';
                filePreview.innerHTML = '';
                uploadBtn.disabled = true;
                progressFill.style.width = '0%';
                progressText.textContent = '0%';
            }, 500);
        }
    }, 200);
});

// Search Functionality
const selectedTagsContainer = document.getElementById('selectedTags');
const searchTags = new Map();

document.getElementById('addTagBtn').addEventListener('click', () => {
    const tag = document.getElementById('tagInput').value.trim().toLowerCase();
    const count = parseInt(document.getElementById('countInput').value) || 1;
    
    if (tag && !searchTags.has(tag)) {
        searchTags.set(tag, count);
        updateTagDisplay();
        document.getElementById('tagInput').value = '';
        document.getElementById('countInput').value = '1';
    }
});

function updateTagDisplay() {
    selectedTagsContainer.innerHTML = '';
    searchTags.forEach((count, tag) => {
        const chip = document.createElement('div');
        chip.className = 'tag-chip';
        chip.innerHTML = `
            ${tag} (≥${count})
            <button onclick="removeTag('${tag}')">×</button>
        `;
        selectedTagsContainer.appendChild(chip);
    });
}

function removeTag(tag) {
    searchTags.delete(tag);
    updateTagDisplay();
}

// Search by tags
document.getElementById('searchByTagsBtn').addEventListener('click', () => {
    if (searchTags.size === 0) {
        alert('Please add at least one tag to search');
        return;
    }
    
    // Mock search results
    displaySearchResults(MOCK_DATA.searchResults);
});

// Search by file
document.getElementById('searchByFileBtn').addEventListener('click', () => {
    const file = document.getElementById('queryFileInput').files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    // Mock: Show all results as if they matched the uploaded file's tags
    displaySearchResults(MOCK_DATA.searchResults);
});

// Search by URL
document.getElementById('searchByUrlBtn').addEventListener('click', () => {
    const url = document.getElementById('thumbnailUrlInput').value.trim();
    if (!url) {
        alert('Please enter a thumbnail URL');
        return;
    }
    
    // Mock: Show a single result
    alert('Full-size image URL: https://example.com/full-size-image.jpg\n(Mock response - backend integration needed)');
});

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p style="text-align: center; color: #666;">No results found</p>';
        return;
    }
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.innerHTML = `
            <img src="${result.thumbnail}" alt="Result">
            <div class="tags">
                ${result.tags.map(tag => `<span class="tag-badge">${tag}</span>`).join('')}
            </div>
        `;
        resultItem.onclick = () => showImageModal(result.url, result.tags.join(', '));
        resultsContainer.appendChild(resultItem);
    });
}

// Modal functionality
const modal = document.getElementById('imageModal');
const modalImg = document.getElementById('modalImage');
const modalCaption = document.getElementById('modalCaption');
const closeModal = document.querySelector('.close');

function showImageModal(src, caption) {
    modal.style.display = 'block';
    modalImg.src = src;
    modalCaption.textContent = caption;
}

closeModal.onclick = () => {
    modal.style.display = 'none';
};

window.onclick = (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Show mock current subscriptions in notifications section
    if (document.getElementById('currentTags')) {
        document.getElementById('currentTags').innerHTML = 
            MOCK_DATA.userSubscriptions.map(tag => 
                `<span class="subscription-tag">${tag}</span>`
            ).join('');
    }
});

// Add enter key support for search inputs
document.getElementById('tagInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('addTagBtn').click();
    }
});

document.getElementById('thumbnailUrlInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('searchByUrlBtn').click();
    }
});
