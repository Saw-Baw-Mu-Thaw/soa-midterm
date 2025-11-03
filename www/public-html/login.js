// login.js - Handles login form submission with FastAPI backend

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const loginBtn = loginForm.querySelector('button[type="submit"]');

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Clear any previous error messages
        hideError();

        // Get form values
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        // Basic validation
        if (!username || !password) {
            showError('Please enter both username and password');
            return;
        }

        // Disable button and show loading state
        setLoadingState(true);

        try {
            // FastAPI OAuth2 expects form data, not JSON
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            // Send login request to FastAPI backend
            const response = await fetch(`${API_BASE_URL}/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.access_token) {
                // Store access token
                sessionStorage.setItem('access_token', data.access_token);
                sessionStorage.setItem('token_type', data.token_type);

                // Fetch user information
                const userResponse = await fetch(`${API_BASE_URL}/customers/me`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (userResponse.ok) {
                    const user = await userResponse.json();
                    
                    // Store user data in sessionStorage
                    sessionStorage.setItem('user', JSON.stringify(user));
                    sessionStorage.setItem('username', user.username);

                    // FIXED: Redirect to payment page with correct path
                    console.log('Login successful, redirecting to payment form...');
                    window.location.href = './index.html';
                } else {
                    showError('Failed to retrieve user information');
                }
            } else {
                // Show error message
                showError(data.detail || 'Invalid username or password');
            }

        } catch (error) {
            console.error('Login error:', error);
            showError('Connection error. Please check if the backend server is running on port 8000.');
        } finally {
            // Re-enable button
            setLoadingState(false);
        }
    });

    // Helper function to show error messages
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        // Auto-hide error after 5 seconds
        setTimeout(hideError, 5000);
    }

    // Helper function to hide error messages
    function hideError() {
        errorMessage.style.display = 'none';
        errorMessage.textContent = '';
    }

    // Helper function to set loading state
    function setLoadingState(loading) {
        if (loading) {
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<span class="loading"></span>Logging in...';
        } else {
            loginBtn.disabled = false;
            loginBtn.innerHTML = 'Login';
        }
    }

    // Add Enter key support for better UX
    document.getElementById('password').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });
});