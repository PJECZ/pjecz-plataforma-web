/* Datatables Filtros */
const UPPER = "UPPER";
const LOWER = "LOWER";

class FiltrosDataTable {
  // Constructor
  constructor(dataTable, configDataTable) {
    this.dataTable = dataTable;
    this.configDataTable = configDataTable;
    this.inputs = [];
  }

  // Agregar un campo input para su procesamiento
  agregarInput(elementById, dataName, caseSensitive = UPPER) {
    let input = {
      object: NaN,
      data_name: "",
      value: "",
      case: "UPPER",
    };
    input.object = document.getElementById(elementById);
    input.data_name = dataName;
    input.case = caseSensitive;
    this.inputs.push(input);
  }

  // Agregar un campo select para su procesamiento
  agregarSelect(elementById, dataName) {
    let select = {
      object: NaN,
      data_name: "",
      value: "",
    };
    select.object = document.getElementById(elementById);
    select.data_name = dataName;
    this.inputs.push(select);
  }

  // Agregar un valor constante
  agregarConstante(dataName, value) {
    let input = {
      object: NaN,
      data_name: "",
      value: "",
      case: NaN,
    };
    input.data_name = dataName;
    input.value = value;
    this.inputs.push(input);
  }

  // Leer los valores de los inputs
  leerValoresInputs() {
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
  }

  // Limpiar los valores de los inputs
  limpiar() {
    for (let i = 0; i < this.inputs.length; i++) {
      if (i.object == NaN) continue;
      delete this.configDataTable["ajax"]["data"][this.inputs[i].data_name];
      // Si es tipo select elimina la option seleccionada
      if (
        this.inputs[i].object.nodeName == "SELECT" &&
        this.inputs[i].object.classList.contains("js-select2-filter")
      ) {
        this.inputs[i].object.textContent = "";
        this.inputs[i].object.options[0] = null;
      }
    }
    // Actualizar el DataTable
    $(this.dataTable).DataTable().destroy();
    $(this.dataTable).DataTable(this.configDataTable);
  }

  // Buscar
  buscar() {
    this.leerValoresInputs();
    // Actualizar el DataTable
    $(this.dataTable).DataTable().destroy();
    $(this.dataTable).DataTable(this.configDataTable);
  }

  // Precargar
  precargar() {
    $(this.dataTable).DataTable(this.configDataTable);
  }
}
