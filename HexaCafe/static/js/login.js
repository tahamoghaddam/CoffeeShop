document.addEventListener('DOMContentLoaded', function() {
    // Function to handle login form submission
    function handleLogin(event) {
        event.preventDefault(); // Prevent default form submission

        const usernameOrEmail = document.getElementById('username_or_email').value;
        const password = document.getElementById('password').value;

        const data = {
            username_or_email: usernameOrEmail,
            password: password
        };

        fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Login successful
                    if (data.is_staff) {
                        location.replace('/admin/'); // Redirect to admin panel if user is staff
                    } else {
                        location.replace('/home/'); // Redirect to home page for regular users
                    }
                } else {
                    // Login failed
                    alert('Invalid username or password');
                }
            })
            .catch(error => {
                console.error('Error logging in:', error);
            });
    }

    // Select login button and add event listener
    const loginButton = document.querySelector('.rectangle-button');
    loginButton.addEventListener('click', handleLogin);

    // Select sign-up link and add event listener
    const signUpLink = document.querySelector('.sign-up-2');
    signUpLink.addEventListener('click', () => {
        // Redirect to signup page
        window.location.href = '/signup/';
    });
});