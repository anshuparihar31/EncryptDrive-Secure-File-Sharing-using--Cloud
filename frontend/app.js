function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const password = document.getElementById('uploadPassword').value;

    if (!fileInput.files.length || !password) {
        alert("Please select a file and enter a password.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => alert(data.message || data.error));
}

function listFiles() {
    fetch('/list-files')
        .then(response => response.json())
        .then(data => {
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';

            data.files.forEach(file => {
                const listItem = document.createElement('li');
                listItem.textContent = file;
                listItem.onclick = () => downloadFile(file);
                fileList.appendChild(listItem);
            });

            // Show download password input
            document.getElementById('downloadPassword').style.display = 'block';
        });
}

function downloadFile(filename) {
    const password = document.getElementById('downloadPassword').value;

    if (!password) {
        alert("Please enter a password to download the file.");
        return;
    }

    const formData = new FormData();
    formData.append('password', password);

    fetch(`/download/${filename}`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.status === 200) {
            return response.blob();
        } else {
            return response.json().then(data => {
                throw new Error(data.error);
            });
        }
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(error => alert(error.message));
}
