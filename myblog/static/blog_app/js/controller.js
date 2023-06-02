class Controller {
    constructor() {
        this.viewElements = {};
        this.Initialize();
    };

    Initialize = () => {
        this.connectDOMElements();
        this.setupListeners();
    };

    connectDOMElements = () => {
        Array.from(document.querySelectorAll('[id]')).map(element => this.viewElements[element.id] = document.getElementById(element.id));
    };

    setupListeners = () => {
        Array.from(document.querySelectorAll('[data-modal-name]')).forEach(btn => btn.addEventListener('click', this.modalInOut));
        this.viewElements['popupTagBtn'].addEventListener('click', () => { this.viewElements['popupTag'].classList.toggle('show') });
    };

    modalInOut = event => {
        let modal = this.viewElements[event.target.dataset.modalName]

        if (modal.id === 'listModalComment') {
            this.viewElements['postId'].value = event.target.dataset.postId;
        }

        if (modal.style.display === 'none' || modal.style.display === '') {
            modal.style.display = 'block';
        } else {
            modal.style.display = 'none';
        };
    };     
};

document.addEventListener('DOMContentLoaded', new Controller());
