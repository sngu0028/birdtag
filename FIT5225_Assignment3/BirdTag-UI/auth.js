// Mock authentication functions
document.getElementById('loginForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    console.log('Login attempt:', { email, password });
    alert('Login functionality will be connected to AWS Cognito\nRedirecting to main app...');
    
    // Mock successful login
    sessionStorage.setItem('mockUser', JSON.stringify({ email, name: 'Test User' }));
    window.location.href = 'index.html';
});

document.getElementById('signupForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        confirmPassword: document.getElementById('confirmPassword').value
    };
    
    if (formData.password !== formData.confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    console.log('Signup attempt:', formData);
    alert('Signup functionality will be connected to AWS Cognito\nPlease check your email to verify your account');
});

document.getElementById('forgotPassword')?.addEventListener('click', (e) => {
    e.preventDefault();
    const email = prompt('Enter your email address:');
    if (email) {
        alert('Password reset functionality will be connected to AWS Cognito\nReset link would be sent to: ' + email);
    }
});
