$(document).ready(function () {
    let startY;
    const swipeThreshold = 50;

    // Initial fetch of the current state
    fetchAndUpdateState();

    // Set up Server-Sent Events
    const eventSource = new EventSource('/stream');
    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        updateUI(data);
    };

    // Handle pray button click
    $('#swipe-prayer').on('click', handlePray);

    // Handle touch events for swipe
    $('#swipe-prayer').on('touchstart', function (e) {
        startY = e.originalEvent.touches[0].clientY;
    });
    // Refresh the site every 10 seconds
    setInterval(function () {
        fetchAndUpdateState();
    }, 10000);

    $('#swipe-prayer').on('touchmove', function (e) {
        if (!startY) return;

        const currentY = e.originalEvent.touches[0].clientY;
        const diff = startY - currentY;

        if (diff > swipeThreshold) {
            handlePray();
            startY = null;
        }
    });

    function fetchAndUpdateState() {
        $.ajax({
            url: '/get_current_rosary_state',
            type: 'GET',
            success: function (response) {
                updateUI(response);
            }
        });
    }

    function handlePray() {
        // Button click animation
        $('#swipe-prayer').addClass('clicked');
        setTimeout(() => {
            $('#swipe-prayer').removeClass('clicked');
        }, 300);

        // Send prayer action
        $.ajax({
            url: '/pray_rosary',
            type: 'POST',
            success: function (response) {
                updateUI(response);
            }
        });
    }

    function updateUI(response) {
        $('#totalRosariesPrayed').text(response.totalRosariesPrayed);
        $('#mysteryType').text(response.mysteryType);
        $('#mysteryName').text(response.mysteryName);

        // Update beads with animation
        for (let i = 1; i <= 10; i++) {
            if (i <= response.currentHailMaryCount) {
                $(`#bead-${i}`).addClass('active');
            } else {
                $(`#bead-${i}`).removeClass('active');
            }
        }

        // Animate cross and red bead when decade is completed
        if (response.currentHailMaryCount === 0 && response.currentDecade > 1) {
            animateCross();
            setTimeout(animateRedBead, 1000);
        }
    }

    function animateCross() {
        $('#cross').addClass('glow');
        setTimeout(() => {
            $('#cross').removeClass('glow');
        }, 1000);
    }

    function animateRedBead() {
        $('#bead-red').addClass('glow');
        setTimeout(() => {
            $('#bead-red').removeClass('glow');
        }, 1000);
    }
});
