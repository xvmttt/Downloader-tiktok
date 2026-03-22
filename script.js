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
        if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.id = 'result';
            downloadBtn.parentNode.insertBefore(resultDiv, downloadBtn.nextSibling);
        }

        const directUrl = data.download_url;

        resultDiv.innerHTML = `
            <div style="margin-top: 30px; text-align: center; padding: 25px; background: #1a1a1a; border-radius: 20px; border: 1px solid #fe2c55;">
                <h4 style="color: white; margin-bottom: 15px; font-family: sans-serif;">Видео готово!</h4>
                
                <a href="${directUrl}" target="_blank" rel="noopener noreferrer" 
                style="display: inline-block; padding: 15px 35px; background: #fe2c55; color: white; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(254, 44, 85, 0.4); transition: transform 0.2s;">
                СКАЧАТЬ MP4
                </a>

                <div style="color: #aaa; font-size: 12px; margin-top: 20px; line-height: 1.5;">
                    <p>⚠️ TikTok запрещает просмотр внутри других сайтов.</p>
                    <p>Если после нажатия видео просто открылось в новой вкладке:</p>
                    <p><b>Нажмите на него правой кнопкой мыши → "Сохранить видео как..."</b></p>
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
