// app/static/js/form_handler.js

document.addEventListener('DOMContentLoaded', () => {
    // Find all forms that should have a loading spinner on submit
    const formsToHandle = document.querySelectorAll('.loading-on-submit');

    formsToHandle.forEach(form => {
        form.addEventListener('submit', (event) => {
            // Find the submit button within this specific form
            const submitButton = form.querySelector('button[type="submit"]');

            // If a button is found, disable it and show the loading state
            if (submitButton) {
                // Prevent multiple clicks
                submitButton.disabled = true;

                // Store the original content of the button
                const originalContent = submitButton.innerHTML;

                // Replace the button content with a spinner and text
                submitButton.innerHTML = `
                    <div class="loader"></div>
                    Processing...
                `;

                // Optional: If the server takes too long, you might want to re-enable the button
                // This is an advanced feature, but good to know about.
                // For now, the page navigation will handle "hiding" the spinner.
            }
        });
    });
});