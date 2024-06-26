document.getElementById('signupButton').addEventListener('click', function(event) {
    event.preventDefault(); // جلوگیری از ارسال فرم به صورت پیش‌فرض

    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var errorDiv = document.getElementById('error');

    // پاک کردن پیام خطای قبلی
    errorDiv.textContent = '';

    // ارسال درخواست به سرور
    fetch('/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // برای ارسال CSRF token در درخواست‌های POST
            },
            body: JSON.stringify({
                name: name,
                email: email,
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Signup was successful!');
                window.location.href = '/login/';
            } else {
                errorDiv.textContent = data.error;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorDiv.textContent = 'Please try again';
        });
});

// تابع برای دریافت CSRF token
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

// افزودن رویداد کلیک به دکمه BACK
document.getElementById('backButton').addEventListener('click', function() {
    window.location.href = '/login/';
});