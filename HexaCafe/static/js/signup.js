document.addEventListener("DOMContentLoaded", function() {
    const signupButton = document.getElementById("signupButton");
    const errorDiv = document.getElementById("error");

    signupButton.addEventListener("click", function() {
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    username: username,
                    password: password
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    window.location.href = '/login/';
                } else if (data.error) {
                    errorDiv.innerHTML = "";
                    const errors = JSON.parse(data.error);
                    for (let key in errors) {
                        if (errors.hasOwnProperty(key)) {
                            const errorMessages = errors[key].map(err => `<p>${err.message}</p>`).join('');
                            errorDiv.innerHTML += `<p><strong>${key}:</strong> ${errorMessages}</p>`;
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                errorDiv.innerHTML = `<p>${error.message}</p>`;
            });
    });
});