class Config {
    adjustLayout() {
        const html = document.getElementsByTagName("html")[0];
        html.setAttribute("data-sidebar-view", window.innerWidth <= 1024 ? "mobile" : "default");
        html.setAttribute("data-profile-view", window.innerWidth <= 1024 ? "mobile" : "default");
    }

    initWindowSize() {
        window.addEventListener('resize', () => this.adjustLayout());
    }

    init() {
        this.adjustLayout();
        this.initWindowSize();
    }
}

new Config().init();
