document.addEventListener('DOMContentLoaded', function() {
    // Password toggle functionality for login modal
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            // Toggle the type attribute
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle the eye icon
            const icon = this.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        });
    }

    // Auto-focus username input when modal opens
    const loginModalElement = document.getElementById('loginModal');
    if (loginModalElement) {
        loginModalElement.addEventListener('shown.bs.modal', function() {
            document.getElementById('username').focus();
        });
    }
    
    // Add subtle entrance animations to bucket cards and info cards
    const animatedElements = document.querySelectorAll('.bucket-card, .info-card, .welcome-card');
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(15px)';
        element.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});
