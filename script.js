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
        body: JSON.stringify({
            url: url         
        })
    })
    .then(response => {
    
    return response.json().then(data => {
        if (!response.ok) {
            throw new Error(data.message || "Ошибка сервера");
        }
        return data; 
    });
    })
    .then(data => {
        try{
            let resultDiv = document.getElementById('result');
            if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.id = 'result';
            document.body.appendChild(resultDiv);
            }

            resultDiv.innerHTML = `
                <div style="margin-top: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 12px; text-align: center;">
                    <h4>${data.title}</h4>
                    <a href="${data.download_url}" target="_blank" rel="noopener noreferrer" 
                    style="display: inline-block; padding: 10px 20px; background: #fe2c55; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Открыть видео напрямую
                    </a>
                    <p style="font-size: 12px; color: gray; margin-top: 8px;">Если видео не качается сразу: нажми на плеер правой кнопкой -> "Сохранить видео как"</p>
                </div>
            `;

        }catch (renderError) {
            console.error("Ошибка при отрисовке видео:", renderError);
        }
    })
    .catch(error =>{
        console.error('Детали:', error);
        showAlert(error.message);
    })
};

function showAlert(message) {
    alertMessage.textContent = message;
    customAlert.style.display = "flex";
}

closeAlert.addEventListener("click", () => {
    customAlert.style.display = "none";
});
