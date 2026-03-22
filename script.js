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
            const mainBtn = document.querySelector('button');
            mainBtn.parentNode.insertBefore(resultDiv, mainBtn.nextSibling);
        }

        resultDiv.innerHTML = `
            <div style="margin-top: 30px; text-align: center; padding: 25px; background: #1a1a1a; border-radius: 20px; border: 2px solid #00f2ea;">
                <h4 style="color: white; margin-bottom: 5px;">${data.title}</h4>
                <p style="color: #00f2ea; margin-bottom: 20px;">Автор: ${data.author}</p>
                
                <a href="${data.download_url}" 
                target="_blank" 
                download="video.mp4"
                style="display: inline-block; padding: 15px 35px; background: linear-gradient(45deg, #fe2c55, #25f4ee); color: black; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(37, 244, 238, 0.3);">
                СКАЧАТЬ БЕЗ ВОДЯНОГО ЗНАКА
                </a>

                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                    Если видео открылось в браузере — нажмите "три точки" и выберите <b>Скачать</b>.
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
