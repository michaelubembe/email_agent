document.addEventListener('DOMContentLoaded', function () {
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const processBtn = document.getElementById('processBtn');
    const statusMessage = document.getElementById('statusMessage');
    const loginSection = document.getElementById('loginSection');
    const processSection = document.getElementById('processSection');
    const userInfo = document.getElementById('userInfo');
    const userEmail = document.getElementById('userEmail');

    // Check authentication status on load
    checkAuthStatus();

    loginBtn.addEventListener('click', async function () {
        loginBtn.disabled = true;
        loginBtn.classList.add('loading');

        try {
            const response = await fetch('/api/auth/login');
            const data = await response.json();

            if (data.auth_url) {
                // Redirect to Google OAuth
                window.location.href = data.auth_url;
            } else {
                showMessage('Failed to initiate login', 'error');
                loginBtn.classList.remove('loading');
                loginBtn.disabled = false;
            }
        } catch (error) {
            showMessage('Failed to connect to server. Please try again.', 'error');
            loginBtn.classList.remove('loading');
            loginBtn.disabled = false;
            console.error('Error:', error);
        }
    });

    logoutBtn.addEventListener('click', async function () {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            showMessage('Logged out successfully', 'info');
            updateUIForAuth(false);
        } catch (error) {
            showMessage('Failed to logout', 'error');
            console.error('Error:', error);
        }
    });

    processBtn.addEventListener('click', async function () {
        // Disable button and show loading state
        processBtn.disabled = true;
        processBtn.classList.add('loading');

        // Hide previous status message
        statusMessage.classList.remove('show', 'success', 'error', 'info');
        statusMessage.textContent = '';

        try {
            const response = await fetch('/api/process-emails', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            // Remove loading state
            processBtn.classList.remove('loading');
            processBtn.disabled = false;

            // Show status message
            if (response.ok && data.success) {
                if (data.count === 0) {
                    showMessage(data.message, 'info');
                } else {
                    showMessage(data.message, 'success');
                }
            } else {
                if (response.status === 401) {
                    showMessage('Please login to continue', 'error');
                    updateUIForAuth(false);
                } else {
                    showMessage(data.message || data.detail || 'An error occurred', 'error');
                }
            }
        } catch (error) {
            // Remove loading state
            processBtn.classList.remove('loading');
            processBtn.disabled = false;

            // Show error message
            showMessage('Failed to connect to server. Please try again.', 'error');
            console.error('Error:', error);
        }
    });

    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();

            if (data.authenticated) {
                userEmail.textContent = data.email;
                updateUIForAuth(true);
            } else {
                updateUIForAuth(false);
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            updateUIForAuth(false);
        }
    }

    function updateUIForAuth(isAuthenticated) {
        if (isAuthenticated) {
            loginSection.style.display = 'none';
            processSection.style.display = 'block';
            userInfo.style.display = 'flex';
        } else {
            loginSection.style.display = 'block';
            processSection.style.display = 'none';
            userInfo.style.display = 'none';
        }
    }

    function showMessage(message, type) {
        statusMessage.textContent = message;
        statusMessage.classList.add('show', type);

        // Auto-hide after 10 seconds
        setTimeout(() => {
            statusMessage.classList.remove('show');
        }, 10000);
    }
});
