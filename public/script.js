
async function extractImages() {
    const urlInput = document.getElementById('urlInput');
    const extractBtn = document.getElementById('extractBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('loader');
    const resultSection = document.getElementById('resultSection');
    const statusMsg = document.getElementById('statusMsg');

    const url = urlInput.value.trim();
    if (!url) {
        statusMsg.innerText = "Please enter a valid URL.";
        return;
    }

    // PROTOCOL CHECK: PREVENT FILE:// ACCESS
    if (window.location.protocol === 'file:') {
        statusMsg.style.color = '#e74c3c';
        statusMsg.innerHTML = `
            <strong>⚠️ CONFIGURATION ERROR</strong><br>
            You are opening this file directly. This prevents the API from working.<br><br>
            Please open this URL in your browser instead:<br>
            <a href="http://localhost:3000" style="color: blue; text-decoration: underline;">http://localhost:3000</a>
        `;
        return;
    }

    // Reset UI
    statusMsg.innerText = "";
    resultSection.innerHTML = "";
    resultSection.style.display = 'grid';

    // Loading State
    extractBtn.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';

    // Show Dino Game to pass time
    document.getElementById('dinoGame').style.display = 'block';

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (response.ok && data.product_images && data.product_images.length > 0) {
            renderImages(data.product_images);
            statusMsg.style.color = 'green';
            statusMsg.innerText = `Success! Found ${data.total_images} images via ${data.strategy_used || 'Agent 7K'}`;
        } else {
            statusMsg.style.color = '#e74c3c';
            statusMsg.innerText = data.message || "No images found visually. The page might be empty or blocked.";
        }

    } catch (error) {
        // Show Error Info
        statusMsg.innerText = "Error: " + (error.message || "Failed to contact server.");
        console.error(error);
    } finally {
        // Reset Button
        extractBtn.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
}

function renderImages(images) {
    const resultSection = document.getElementById('resultSection');

    // Create Image Cards (Clean, no buttons)
    const html = images.map(imgUrl => `
        <div class="image-card">
            <img src="${imgUrl}" loading="lazy" alt="Product Image" onerror="this.style.display='none'">
        </div>
    `).join('');

    resultSection.innerHTML = html;
    resultSection.style.display = 'grid';

    // Show Success Notification
    showToast();
}

function showToast() {
    const toast = document.getElementById('toast');
    toast.classList.add('show');

    // Play Notification Sound (Optional/Subtle)
    try {
        const audio = new Audio('https://assets.mixkit.co/sfx/preview/mixkit-software-interface-start-2574.mp3');
        audio.volume = 0.5;
        audio.play();
    } catch (e) { }

    // Hide after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}
