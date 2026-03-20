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
        <div style="margin-top: 30px; text-align: center; padding: 20px; background: #1a1a1a; border-radius: 15px; border: 1px solid #fe2c55;">
            <h4 style="color: white; margin-bottom: 20px;">Видео найдено!</h4>
            
            <a href="${directUrl}" target="_blank" rel="noopener noreferrer" 
               style="display: inline-block; padding: 15px 30px; background: #fe2c55; color: white; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(254, 44, 85, 0.5);">
               СКАЧАТЬ MP4
            </a>

            <p style="color: #888; font-size: 13px; margin-top: 20px;">
                Нажмите на кнопку, видео откроется в новой вкладке.<br>
                Затем нажмите <b>правой кнопкой мыши</b> (или зажмите пальцем) и выберите <b>"Сохранить видео"</b>.
            </p>
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
