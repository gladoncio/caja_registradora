
document.addEventListener("DOMContentLoaded", function () {
    // Obtén el checkbox y los elementos que deseas cambiar
    const switchInput = document.getElementById("Switch");
    const elementos = {
        accordionSidebar: document.getElementById("accordionSidebar"),
        nav: document.getElementById("nav"),
        usernametext: document.getElementById("usernametext"),
        footerChange: document.getElementById("footer-change"),
        contentWrapper: document.getElementById("content-wrapper"),
        id_barcode: document.getElementById("id_barcode"),
        titulo: document.getElementById("titulo"),
        monto: document.getElementById("monto"),
    };

    // Define los estilos para cada estado (activado y desactivado)
    const estilos = {
        activado: {
            body: ['bg-dark'], 
            accordionSidebar: ["bg-gradient-primary"],
            nav: ["navbar-light", "bg-white", "text-gray-600"],
            usernametext: ["text-gray-600"],
            footerChange: ["bg-white", "text-dark"],
            contentWrapper: ['bg-white','text-gray-600'],
            contentCard: ['bg-white','text-gray-600'],
            contentCardsNoDysplay: ['colorborderlight','bg-white','text-gray-600'],
            id_barcode: ['bg-white','text-gray-600'],
            fondo: ['bg-white'],
            titulo: ['text-gray-600'],
            monto: ['bg-white','text-gray-600'],
            botonDinamico : ['btn-primary'],
            texto : ['text-gray'],

        },
        desactivado: {
            body: ['bg-dark'], 
            accordionSidebar: ["bg-gradient-dark"],
            nav: ["navbar-dark", "bg-dark", "text-white-600"],
            usernametext: ["text-white-600"],
            footerChange: ["bg-dark", "text-white"],
            contentWrapper: ['bg-dark2','text-white'],
            contentCard: ['bg-dark','text-white'],
            contentCardsNoDysplay: ['colorborderdark','bg-dark','text-white'],
            id_barcode: ['bg-dark','text-white'],
            fondo: ['bg-dark'],
            titulo: ['text-white'],
            monto: ['bg-dark','text-white'],
            botonDinamico : ['btn-primaryui'],
            texto : ['text-white'],
        },
    };


    // Función para aplicar estilos según el estado almacenado
    function aplicarEstilos(estado) {
        document.body.classList.remove(...estilos.activado.body, ...estilos.desactivado.body);
        document.body.classList.add(...estilos[estado].body);
        for (const elementoID in elementos) {
            if (elementos.hasOwnProperty(elementoID)) {
                const elementoDOM = elementos[elementoID];
                if (elementoDOM) {
                    const clases = estilos[estado][elementoID] || [];
                    elementoDOM.classList.remove(...estilos.activado[elementoID], ...estilos.desactivado[elementoID]);
                    elementoDOM.classList.add(...clases);
                }
            }
        }

         // Establecer un estilo inicial para el body
        document.body.classList.add(...estilos.desactivado.body);
        
        const btns = document.querySelectorAll('.boton-dinamico');
        btns.forEach(btn => {
            btn.classList.remove(...estilos.activado.botonDinamico, ...estilos.desactivado.botonDinamico);
            btn.classList.add(...estilos[estado].botonDinamico);
        });

        const textos = document.querySelectorAll('.texto');
        textos.forEach(texto => {
            texto.classList.remove(...estilos.activado.texto, ...estilos.desactivado.texto);
            texto.classList.add(...estilos[estado].texto);
        });

        const cards = document.querySelectorAll('.release-card');
        cards.forEach(card => {
            card.classList.remove(...estilos.activado.contentCard, ...estilos.desactivado.contentCard);
            card.classList.add(...estilos[estado].contentCard);
        });

        const cards2 = document.querySelectorAll('.release-card-header');
        cards2.forEach(card => {
            card.classList.remove(...estilos.activado.contentCardsNoDysplay, ...estilos.desactivado.contentCardsNoDysplay);
            card.classList.add(...estilos[estado].contentCardsNoDysplay);
        });

        const fondos = document.querySelectorAll('.solofondo');
        fondos.forEach(text => {
            text.classList.remove(...estilos.activado.fondo, ...estilos.desactivado.fondo);
            text.classList.add(...estilos[estado].fondo);
        });

        const inputs = document.querySelectorAll('.onlyinput');
        inputs.forEach(input => {
            input.classList.remove(...estilos.activado.id_barcode, ...estilos.desactivado.id_barcode);
            input.classList.add(...estilos[estado].id_barcode);
        });
    }

    // Recuperar el estado almacenado
    const estadoAlmacenado = localStorage.getItem('estadoSwitch');

 // Aplicar estilos iniciales
    aplicarEstilos(estadoAlmacenado || 'desactivado');
    
 // Asegúrate de que el estado del switch refleje el estado almacenado
    switchInput.checked = estadoAlmacenado === 'activado';

    // Agrega un evento de cambio al checkbox
    switchInput.addEventListener("change", function () {
        const estado = switchInput.checked ? "activado" : "desactivado";
        aplicarEstilos(estado);

        // Guarda el estado en localStorage
        localStorage.setItem('estadoSwitch', estado);
    });
});
