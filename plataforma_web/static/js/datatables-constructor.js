/* Datatables Config */
class ConfigDataTable {
  // Constructor
  constructor(csrf_token) {
    this.csrf_token = csrf_token;
  }

  // Entregar configuracion
  config() {
    return {
      processing: true,
      serverSide: true,
      ordering: false,
      searching: false,
      responsive: true,
      scrollX: true,
      ajax: {
        url: null,
        type: "POST",
        headers: { "X-CSRF-TOKEN": this.csrf_token },
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
}
