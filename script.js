const inputLink = document.getElementById('input-link')
const downloadBtn = document.getElementById('downloadBtn');
const customAlert = document.getElementById('customAlert'); 
const alertMessage = document.getElementById('alertMessage'); 
const closeAlert = document.getElementById('closeAlert');

document.addEventListener('submit', function(e) {
    e.preventDefault();
    return false;
    }, true);
downloadBtn.addEventListener('click', function(event) {
    
    event.preventDefault();
    event.stopPropagation(); 

    const url = inputLink.value.trim();
    
    
    console.log("Кнопка нажата, URL:", url);

    if (!url) {
        showAlert("Введите ссылку!");
        return;
    }

    
    performDownload(url); 
});


function performDownload(url) {
    fetch('https://tiktok-saver-l18l.onrender.com/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => {
        // Мы СНАЧАЛА читаем JSON, а потом проверяем статус
        return response.json().then(data => {
            if (!response.ok) {
                // Если статус не 200, берем сообщение из пришедшего JSON
                throw new Error(data.message || data.error || "Ошибка сервера");
            }
            return data; 
        });
    })
    .then(data => {
        let resultDiv = document.getElementById('result');
        // ... (код проверки resultDiv тот же)

        // Формируем ссылку через твой прокси на Render
        const proxyUrl = `https://tiktok-saver-l18l.onrender.com/proxy_video?url=${encodeURIComponent(data.download_url)}`;

        resultDiv.innerHTML = `
            <div style="margin-top: 20px; text-align: center; background: #111; padding: 15px; border-radius: 15px;">
                <h4 style="color: white; font-size: 14px;">${data.title}</h4>
                <video controls playsinline width="100%" style="max-width: 280px; border-radius: 10px; margin-top: 10px;">
                    <source src="${proxyUrl}" type="video/mp4">
                    Ваш браузер не поддерживает видео.
                </video>
                <div style="margin-top: 15px;">
                    <a href="${proxyUrl}" download="tiktok_video.mp4" 
                    style="display: inline-block; padding: 10px 25px; background: #fe2c55; color: white; text-decoration: none; border-radius: 25px; font-weight: bold;">
                    СКАЧАТЬ MP4
                    </a>
                </div>
            </div>
        `;
})
    .catch(error => {
        console.error('Детали:', error);
        showAlert(error.message);
    });
}

function showAlert(message) {
    alertMessage.textContent = message;
    customAlert.style.display = "flex";
}

closeAlert.addEventListener("click", () => {
    customAlert.style.display = "none";
});
