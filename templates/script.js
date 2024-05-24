// function startProcessing(index) {
//     fetch(`/start/${index}`, { method: 'POST' })
//         .then(response => response.text())
//         .then(result => {
//             console.log(result);
//             document.getElementById(`video${index + 1}`).src = `/video_feed/${index}`;
//         })
//         .catch(error => console.error(`Erro ao iniciar o processo ${index + 1}:`, error));
// }

// function stopProcessing(index) {
//     fetch(`/stop/${index}`, { method: 'POST' })
//         .then(response => response.text())
//         .then(result => {
//             console.log(result);
//             document.getElementById(`video${index + 1}`).src = '';
//         })
//         .catch(error => console.error(`Erro ao parar o processo ${index + 1}:`, error));
// }