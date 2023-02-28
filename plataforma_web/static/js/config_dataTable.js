function ConfigDataTable(csrf_token) {
  this.config = {
    processing: true,
    serverSide: true,
    ordering: false,
    searching: false,
    responsive: true,
    scrollX: true,
    ajax: {
      url: null,
      type: "POST",
      headers: { "X-CSRF-TOKEN": csrf_token },
      dataType: "json",
      dataSrc: "data",
      data: null,
    },
    columns: null,
    columnDefs: null,
    language: {
      lengthMenu: "Mostrar _MENU_",
      search: "Filtrar:",
      zeroRecords: "No se encontraron registros",
      info: "Total de registros _TOTAL_ ",
      infoEmpty: "No hay registros",
      infoFiltered: "(_TOTAL_ filtrados de _MAX_ registros)",
      oPaginate: {
        sFirst: "Primero",
        sLast: "Último",
        sNext: "Siguiente",
        sPrevious: "Anterior",
      },
    },
  };

  /* Renderiza una celda de la tabla con el texto indicado haciéndolo un enlace a la url indicada
  y dejando el texto plano si el enlace está vacío. */
  this.texto_con_url = function (texto, url) {
    if (url == "") return texto;
    return '<a href="' + url + '">' + texto + "</a>";
  };

  /* Corta el texto a una longitud especificada, al pasar de ésta, agrega la puntuación '…' al final */
  this.texto_cortado = function (texto, longitud = 32) {
    return texto.length > longitud ? texto.substr(0, longitud) + "…" : texto;
  };
}
