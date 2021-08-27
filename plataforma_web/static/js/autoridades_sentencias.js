// autoridades_sentencias.js

// Debe definir los parametros como variables
function obtener_autoridades_sentencias(path_json, container_id, spinner_id) {

    // Se hace la peticion y se espera su respuesta
    fetch(path_json).then((promesa) => {
        promesa.json().then((entrada) => {

            // Icono
            var icono = document.createElement('span');
            icono.classList.add('iconify');
            icono.setAttribute("data-icon", 'mdi:calendar-month');
            var icono_boton = document.createElement('div');
            icono_boton.classList.add('feature-icon');
            icono_boton.classList.add('bg-primary');
            icono_boton.classList.add('bg-gradient');
            icono_boton.appendChild(icono);

            // Titulo
            var titulo = document.createElement('h3');
            titulo.classList.add('card-title');
            titulo.innerText = entrada.titulo;

            // Breve
            var breve = document.createElement('p');
            breve.classList.add('card-text');
            breve.innerText = 'Breve comentario.';

            // Cuerpo = Icono + Titulo + Breve
            var cuerpo = document.createElement('div');
            cuerpo.classList.add('card-body');
            cuerpo.appendChild(icono_boton);
            cuerpo.appendChild(titulo);
            cuerpo.appendChild(breve);

            // Tarjeta = Cuerpo + Listado
            var tarjeta = document.createElement('div');
            tarjeta.appendChild(cuerpo);
            //tarjeta.appendChild(listado);
            tarjeta.classList.add('card');

            // Poner en el contenedor
            $(container_id).append(tarjeta);

            // Ocultar el spinner
            $(spinner_id).hide();

        });
    });

}
