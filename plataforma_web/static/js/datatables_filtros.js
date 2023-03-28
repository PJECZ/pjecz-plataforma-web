class Filtros {
  constructor(dataTable, configDataTable) {
    const UPPER = "UPPER";
    const LOWER = "LOWER";
    this.dataTable = dataTable;
    this.configDataTable = configDataTable;
    this.inputs = [];

    // Añada un campo input para su procesamiento
    this.add_input = function (
      elementById_input,
      data_name,
      case_sensitive = UPPER
    ) {
      let input = {
        object: NaN,
        data_name: "",
        value: "",
        case: "UPPER",
      };
      input.object = document.getElementById(elementById_input);
      input.data_name = data_name;
      input.case = case_sensitive;

      this.inputs.push(input);
    };

    this.lecturaValoresInputs = function () {
      // Extrae el valor de los inputs
      for (let i = 0; i < this.inputs.length; i++) {
        switch (this.inputs[i].case) {
          case UPPER:
            this.inputs[i].value = this.inputs[i].object.value.toUpperCase();
            break;
          case LOWER:
            this.inputs[i].value = this.inputs[i].object.value.toLowerCase();
            break;
          default:
            this.inputs[i].value = this.inputs[i].object.value;
        }
        // Si está vacío lo omite y busca en los demás
        if (this.inputs[i].value == "")
          delete this.configDataTable["ajax"]["data"][this.inputs[i].data_name];
        else
          this.configDataTable["ajax"]["data"][this.inputs[i].data_name] =
            this.inputs[i].value;
      }
    };

    this.limpiar = function () {
      // Elimina todos los valore enviados
      for (let i = 0; i < this.inputs.length; i++) {
        delete this.configDataTable["ajax"]["data"][this.inputs[i].data_name];
        // Si es tipo select elimina la option seleccionada.
        if (this.inputs[i].object.nodeName == 'SELECT' && this.inputs[i].object.classList.contains('js-select2-filter')) {
          this.inputs[i].object.textContent = '';
          this.inputs[i].object.options[0] = null;
        }
      }

      // Destruir option en caso de ser un input select
      /*document.getElementById('juzgadoInput_remesa').textContent = '';
      document.getElementById('juzgadoInput_remesa').options[0] = null;*/

      // Actualiza los resultados en el DataTable
      $(this.dataTable).DataTable().destroy();
      $(this.dataTable).DataTable(this.configDataTable);
    };

    this.buscar = function () {
      this.lecturaValoresInputs();
      // Actualiza los resultados en el DataTable
      $(this.dataTable).DataTable().destroy();
      $(this.dataTable).DataTable(this.configDataTable);
    };

    this.precarga = function () {
      //this.lecturaValoresInputs();
      $(this.dataTable).DataTable(this.configDataTable);
    };
  }
}
