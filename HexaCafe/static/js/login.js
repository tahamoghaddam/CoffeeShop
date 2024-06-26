document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username_or_email = document.getElementById('username_or_email').value;
    var password = document.getElementById('password').value;
    var errorDiv = document.getElementById('error');
    var submitButton = document.querySelector('.rectangle-button');


    errorDiv.textContent = '';


    submitButton.classList.remove('animateButton');


    fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                username_or_email: username_or_email,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Login was successful!');

            } else {
                errorDiv.textContent = data.error;

                submitButton.classList.add('animateButton');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorDiv.textContent = 'Please try again!';
        });
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.getElementById('signUpButton').addEventListener('click', function() {
    window.location.href = '/register/';
});