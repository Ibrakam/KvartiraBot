// Показываем количество выбранных файлов
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.querySelector('input[name="upload_images"]');

        if (fileInput) {
            // Создаем элемент для отображения информации о выбранных файлах
            const infoDiv = document.createElement('div');
            infoDiv.style.marginTop = '10px';
            infoDiv.style.padding = '8px';
            infoDiv.style.backgroundColor = '#e7f3ff';
            infoDiv.style.border = '1px solid #b3d9ff';
            infoDiv.style.borderRadius = '4px';
            infoDiv.style.display = 'none';
            fileInput.parentElement.appendChild(infoDiv);

            // Обработчик изменения файлов
            fileInput.addEventListener('change', function() {
                const filesCount = this.files.length;

                if (filesCount > 0) {
                    let fileNames = [];
                    for (let i = 0; i < Math.min(filesCount, 3); i++) {
                        fileNames.push(this.files[i].name);
                    }

                    let message = `Выбрано файлов: <strong>${filesCount}</strong>`;
                    if (filesCount > 10) {
                        message += ' <span style="color: #d63031;">(будут загружены первые 10)</span>';
                    }
                    message += '<br><small>' + fileNames.join(', ');
                    if (filesCount > 3) {
                        message += ` и еще ${filesCount - 3}...`;
                    }
                    message += '</small>';

                    infoDiv.innerHTML = message;
                    infoDiv.style.display = 'block';
                } else {
                    infoDiv.style.display = 'none';
                }
            });
        }
    });
})();
