    document.querySelector("form").addEventListener("submit", function(event) {
        const password = document.querySelector("[name='password']").value;
        const confirmPassword = document.querySelector("[name='confirm_password']").value;
    
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            event.preventDefault(); // Prevent form submission
        }
    });
    