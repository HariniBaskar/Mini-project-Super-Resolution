document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const enhanceButton = document.getElementById('enhance-button');
    const resultSection = document.getElementById('result-section');
    const originalImage = document.getElementById('original-image');
    const enhancedImage = document.getElementById('enhanced-image');
    const downloadButton = document.getElementById('download-button');
    const loadingOverlay = document.getElementById('loading-overlay');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (fileInput.files.length === 0) {
            alert('Please select an image first.');
            return;
        }
        
        const formData = new FormData(this);
        
        // Display original image
        const file = fileInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            originalImage.src = e.target.result;
        }
        reader.readAsDataURL(file);

        // Show loading overlay
        loadingOverlay.style.display = 'flex';

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            enhancedImage.src = url;
            resultSection.style.display = 'block';
            downloadButton.href = url;
            downloadButton.download = 'enhanced_image.jpg';
            loadingOverlay.style.display = 'none';
        })
        .catch(error => {
            console.error('Error:', error);
            loadingOverlay.style.display = 'none';
            alert('An error occurred while enhancing the image. Please try again.');
        });
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            this.nextElementSibling.textContent = fileName;
        }
    });
});