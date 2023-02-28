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
}
