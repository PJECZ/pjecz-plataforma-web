// autoridades_edictos.js

// Debe definir los parametros como variables
function obtener_autoridades_edictos(path_json, container_id, spinner_id) {

    // Se hace la peticion y se espera su respuesta
    fetch(path_json).then((promesa) => {
        promesa.json().then((entrada) => {

            // Icono
            var icono = document.createElement('span');
            icono.classList.add('iconify');
            icono.setAttribute("data-icon", 'mdi:file-check');
            var icono_boton = document.createElement('div');
            icono_boton.classList.add('feature-icon');
            icono_boton.classList.add('bg-primary');
            icono_boton.classList.add('bg-gradient');
            icono_boton.appendChild(icono);
            var icono_vinculo = document.createElement('a');
            icono_vinculo.appendChild(icono_boton);
            icono_vinculo.href = entrada.url;

            // Listado de edictos
            var los_edictos = entrada.listado;
            var listado = document.createElement('ul');
            for (var i = 0; i < los_edictos.length; i++) {
                var renglon = document.createElement('li');
                renglon.innerText = los_edictos[i].expediente;
                renglon.classList.add('list-group-item');
                listado.appendChild(renglon);
            }
            listado.classList.add('list-group');
            listado.classList.add('list-group-flush');

            // Titulo
            var titulo = document.createElement('h3');
            titulo.classList.add('card-title');
            titulo.innerText = entrada.titulo;
            var titulo_vinculo = document.createElement('a');
            titulo_vinculo.appendChild(titulo);
            titulo_vinculo.href = entrada.url;

            // Breve
            var breve = document.createElement('p');
            breve.classList.add('card-text');
            breve.innerText = entrada.breve;

            // Cuerpo = Icono + Titulo + Breve
            var cuerpo = document.createElement('div');
            cuerpo.classList.add('card-body');
            cuerpo.appendChild(icono_vinculo);
            cuerpo.appendChild(titulo_vinculo);
            cuerpo.appendChild(breve);

            // Tarjeta = Cuerpo + Listado
            var tarjeta = document.createElement('div');
            tarjeta.appendChild(cuerpo);
            tarjeta.appendChild(listado);
            tarjeta.classList.add('card');

            // Poner en el contenedor
            $(container_id).append(tarjeta);

            // Ocultar el spinner
            $(spinner_id).hide();

        });
    });

}
