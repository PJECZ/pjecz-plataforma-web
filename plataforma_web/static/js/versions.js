// versions.js

// Cuando se haya terminado la carga de la pagina
$(document).ready(function () {

    // Identificador del div donde trabajar
    const contenedor = document.getElementById('versiones_container');

    // Se pide y se espera que se cargue versiones_json
    fetch(versiones_json).then((promesa) => {
        promesa.json().then((entrada) => {
            var las_versiones = entrada.versiones;
            for (var i = 0; i < las_versiones.length; i++) {
                var item = las_versiones[i];

                // Novedades
                las_novedades = item.novedades;
                novedades = document.createElement('dl');
                for (var j = 0; j < las_novedades.length; j++) {
                    var item2 = las_novedades[j]
                    var titulo = document.createElement('dt');
                    titulo.innerText = item2.titulo;
                    var descripcion = document.createElement('dd');
                    descripcion.innerText = item2.descripcion;
                    novedades.appendChild(titulo);
                    novedades.appendChild(descripcion);
                }

                // Numero
                var numero = document.createElement('h2');
                numero.innerText = item.numero;

                // Fecha
                var fecha = document.createElement('p');
                fecha.innerText = item.fecha;

                // Todo junto
                var todo = document.createElement('div');
                todo.appendChild(numero);
                todo.appendChild(fecha);
                todo.appendChild(novedades);

                // Poner en el contenedor
                contenedor.appendChild(todo);
            }
        });

        // Ocultar el spinner
        $('#versiones_spinner').hide();

    });
});
