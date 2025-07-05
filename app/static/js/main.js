// app/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Dark Mode Toggle Logic (existing) ---
    const themeToggleButton = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    if (localStorage.getItem('theme') === 'dark' || 
       (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        htmlElement.classList.add('dark');
    } else {
        htmlElement.classList.remove('dark');
    }

    themeToggleButton.addEventListener('click', () => {
        htmlElement.classList.toggle('dark');
        if (htmlElement.classList.contains('dark')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });

    // --- NEW: Hamburger Menu Logic ---
    const hamburgerButton = document.getElementById('hamburger-button');
    const mobileMenu = document.getElementById('mobile-menu');

    // Check if the elements exist before adding an event listener
    if (hamburgerButton && mobileMenu) {
        hamburgerButton.addEventListener('click', () => {
            // Toggle the 'hidden' class to show/hide the menu
            mobileMenu.classList.toggle('hidden');
        });
    }
});