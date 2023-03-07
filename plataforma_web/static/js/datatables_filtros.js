function Filtros(dataTable, configDataTable) {
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
    for (let i = 0; i < this.inputs.length; i++)
      delete this.configDataTable["ajax"]["data"][this.inputs[i].data_name];

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
