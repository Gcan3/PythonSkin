const fileInput = document.getElementById('file-upload');
const fileLabel = document.getElementById('file-label');

fileInput.addEventListener('change', function (e) {
    const fileName = e.target.value.split('\\').pop(); // Extract filename
    fileLabel.textContent = fileName;
});