document.addEventListener("DOMContentLoaded", function () {
    const tabContents = document.querySelectorAll(".tab-content");

    function clearActiveTabs() {
        document.querySelectorAll(".nav-item[data-tab]").forEach(link => link.classList.remove("active"));
        tabContents.forEach(tab => tab.classList.remove("active"));
    }

    function activateTab(tabId) {
        const targetLink = document.querySelectorAll(`.nav-item[data-tab="${tabId}"]`);
        const targetContent = document.getElementById(tabId);

        if (targetContent) {
            clearActiveTabs();
            targetLink.forEach(link => link.classList.add("active"));
            targetContent.classList.add("active");
            history.replaceState(null, null, `#${tabId}`);
        }
    }

    // Attach event listeners to ALL matching links (sidebar + offcanvas)
    function initTabClicks() {
        const navLinks = document.querySelectorAll(".nav-item[data-tab]");
        navLinks.forEach(link => {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                const selectedTab = this.getAttribute("data-tab");
                activateTab(selectedTab);
            });
        });
    }

    // Call on DOM load
    initTabClicks();

    // Load initial tab from hash
    const initialTab = window.location.hash ? window.location.hash.substring(1) : "overview";
    activateTab(initialTab);

    // Handle hash change (back/forward browser)
    window.addEventListener("hashchange", function () {
        const newTab = window.location.hash.substring(1);
        activateTab(newTab);
    });
});
