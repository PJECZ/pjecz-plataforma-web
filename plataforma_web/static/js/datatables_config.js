class ConfigDataTable {
  constructor(csrf_token) {
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
    this.texto_con_url = function (texto, url, tooltip = null) {
      let texto_html = "";
      if (url == "") texto_html = texto;
      else texto_html = '<a href="' + url + '">' + texto + "</a>";
      if (tooltip != null)
        return '<span title="' + tooltip + '">' + texto_html + "</span>";
      return texto_html;
    };

    /* Corta el texto a una longitud especificada, al pasar de ésta, agrega la puntuación '…' al final */
    this.texto_cortado = function (texto, longitud = 32) {
      if (texto.length > longitud) {
        const texto_cortado = texto.substr(0, longitud) + "…";
        return "<span title='" + texto + "'>" + texto_cortado + "</span>";
      }
      return texto;
    };

    /* Corta el texto a una longitud especificada, al pasar de ésta, agrega la puntuación '…' al final */
    this.texto_con_tooltip = function (texto, tooltip) {
      return "<span title='" + tooltip + "'>" + texto + "</span>";
    };

    /* Texto con formato de tiempo */
    this.texto_tiempo = function (
      texto,
      moment,
      formato = "YYYY-MM-DD HH:mm:ss"
    ) {
      return moment.utc(texto).local().format(formato);
    };
  }
}
