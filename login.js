// static/js/login.js

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            
            // 1. Clear previous errors
            loginError.innerText = '';
            loginError.style.padding = '0';
            loginError.style.backgroundColor = 'transparent';
            
            // 2. Perform validation
            if (username === '' || password === '') {
                // Prevent form submission
                event.preventDefault(); 
                
                // 3. Display error message
                loginError.innerText = '🛑 Error: Both username and password fields must be filled out.';
                
                // Add styling
                loginError.style.padding = '10px';
                loginError.style.backgroundColor = '#ffdddd';
                loginError.style.color = 'red';
                loginError.style.border = '1px solid red';
            } 
        });
    }
});