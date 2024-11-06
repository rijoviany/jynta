function pray(prayerType) {
    const animationContainer = document.getElementById(`${prayerType}Animation`);
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

    if (prayerType === 'stgertrude') {
        for (let i = 0; i < 5; i++) {
            const randomDelay = Math.random() * 2000; // Random delay between 0 and 2 seconds
            createAndAnimateEmoji(randomDelay);
        }
    } else {
        createAndAnimateEmoji();
    }

    fetch(`/pray/${prayerType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`${prayerType}Counter`).textContent = data.count;
        } else {
            console.error(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Event listeners for each prayer button
document.getElementById('soulPrayButton').addEventListener('click', () => pray('soul'));
document.getElementById('creedPrayButton').addEventListener('click', () => pray('creed'));
document.getElementById('hailPrayButton').addEventListener('click', () => pray('hail'));
document.getElementById('rosaryPrayButton').addEventListener('click', () => pray('rosary'));
document.getElementById('wocPrayButton').addEventListener('click', () => pray('woc'));
document.getElementById('blessedPrayButton').addEventListener('click', () => pray('blessed'));
document.getElementById('stgertrudePrayButton').addEventListener('click', () => pray('stgertrude'));

