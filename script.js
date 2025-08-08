document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const testImageContainer = document.getElementById('test-image-container');
    const testImagePreview = document.getElementById('test-image-preview');
    const imageUpload = document.getElementById('image-upload');
    const searchButton = document.getElementById('search-button');
    const resetButton = document.getElementById('reset-button');
    const similarImagesContainer = document.getElementById('similar-images-container');

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
    });

    imageUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                testImagePreview.src = e.target.result;
                testImagePreview.style.display = 'block';
                testImageContainer.querySelector('.upload-icon').style.display = 'none';
                searchButton.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    searchButton.addEventListener('click', () => {
        searchButton.disabled = true;
        searchButton.innerHTML = 'Searching...';

        const formData = new FormData();
        formData.append("image", imageUpload.files[0]);

        fetch('http://localhost:5000/search', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            displaySimilarImages(data);
            searchButton.innerHTML = 'Search Similar Images';
            searchButton.disabled = false;
        })
        .catch(error => {
            console.error("Error:", error);
            searchButton.innerHTML = 'Search Similar Images';
            searchButton.disabled = false;
        });
    });

    resetButton.addEventListener('click', () => {
        testImagePreview.src = '';
        testImagePreview.style.display = 'none';
        testImageContainer.querySelector('.upload-icon').style.display = 'block';
        searchButton.disabled = true;
        imageUpload.value = '';
        similarImagesContainer.innerHTML = '';
    });

    function displaySimilarImages(images) {
        similarImagesContainer.innerHTML = '';
        images.forEach((image, index) => {
            const img = document.createElement('img');
            img.src = `http://localhost:5000${image.path}`;
            img.alt = `Similar Image ${index + 1}`;
            img.className = 'similar-image fade-in';
            img.style.animationDelay = `${index * 0.1}s`;
            similarImagesContainer.appendChild(img);
        });
    }
});