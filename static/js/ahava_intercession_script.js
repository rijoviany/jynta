function pray(prayerType) {
    const id = prayerType.replace('prayer_', '');
    const animationContainer = document.getElementById(`prayerAnimation_${id}`);
    if (!animationContainer) return;

    const createAndAnimateEmoji = (delay = 0) => {
        setTimeout(() => {
            const soul = document.createElement('img');
            soul.classList.add('soul');

            const randomNumber = Math.floor(Math.random() * 70) + 1;
            soul.src = `/static/images/${randomNumber}.png`;

            const randomX = Math.random() * 80 + 10;
            soul.style.left = randomX + '%';

            animationContainer.appendChild(soul);

            setTimeout(() => {
                soul.remove();
            }, 3000);
        }, delay);
    };

    createAndAnimateEmoji();

    fetch(`/intercession/${prayerType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const counterElement = document.getElementById(`prayerCounter_${id}`);
            if (counterElement) {
                counterElement.textContent = data.count;
                // Update progress bar
                const progressBar = counterElement.closest('.prayer-counter').querySelector('.progress-bar');
                const counterText = counterElement.parentElement.textContent;
                const target = parseInt(counterText.split('/')[1].trim());
                const progress = Math.min((data.count / target * 100), 100);
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.textContent = `${progress.toFixed(1)}%`;
            }
        } else {
            console.error(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Add event listener when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    const prayButton = document.getElementById('prayButton');
    if (prayButton) {
        prayButton.addEventListener('click', function() {
            const prayerType = this.getAttribute('data-prayer-type');
            pray(prayerType);
        });
    }
}); 