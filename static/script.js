function startProcessing() {
    fetch('/start')
        .then(response => {
            if (response.ok) {
                document.getElementById('video').src = '/video_feed';
            }
        })
        .catch(error => console.error('Error starting process:', error));
}

function stopProcessing() {
    fetch('/stop')
        .then(response => {
            if (response.ok) {
                document.getElementById('video').src = '';
            }
        })
        .catch(error => console.error('Error stopping process:', error));
}
