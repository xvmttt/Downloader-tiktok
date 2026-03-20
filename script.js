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
        try {
            let resultDiv = document.getElementById('result');
            if (!resultDiv) {
                resultDiv = document.createElement('div');
                resultDiv.id = 'result';
                document.body.appendChild(resultDiv);
            }

            const proxyUrl = `https://tiktok-saver-l18l.onrender.com/proxy_video?url=${encodeURIComponent(data.download_url)}`;

            resultDiv.innerHTML = `
                <div style="margin-top: 20px; text-align: center;">
                    <h4>${data.title}</h4>
                    <video controls width="100%" style="max-width: 300px; border-radius: 8px;">
                        <source src="${proxyUrl}" type="video/mp4">
                    </video>
                    <br><br>
                    <a href="${proxyUrl}" 
                       style="padding: 10px 20px; background: #fe2c55; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                       Скачать видео
                    </a>
                </div>
            `;
        } catch (renderError) {
            console.error("Ошибка при отрисовке:", renderError);
        }
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
