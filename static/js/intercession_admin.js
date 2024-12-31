document.addEventListener('DOMContentLoaded', function() {
    // Handle Edit Button Click
    document.querySelectorAll('.edit-prayer').forEach(button => {
        button.addEventListener('click', function() {
            const prayerId = this.dataset.id;
            // Implement edit functionality
            console.log('Edit prayer:', prayerId);
        });
    });

    // Handle Toggle Status
    document.querySelectorAll('.toggle-status').forEach(button => {
        button.addEventListener('click', function() {
            const prayerId = this.dataset.id;
            const currentActive = this.dataset.active === 'true';
            
            fetch('/intercession-admin/toggle-status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prayer_id: prayerId,
                    active: !currentActive
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
}); 