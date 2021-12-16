// cid_procedimientos.js

// Guardar Encabezado
function guardar_encabezado() {
    titulo_procedimiento = $('#titulo_procedimiento').val();
    codigo = $('#codigo').val();
    revision = $('#revision').val();
    fecha = $('#fecha').val();
}

// Guardar Objetivo
function guardar_objetivo() {
    objetivo = JSON.stringify(objetivoQuill.getContents());
    $('#objetivo').val(objetivo);
}

// Llenar Objetivo
function llenar_objetivo(contenido) {
    objetivoQuill.setContents(contenido);
}

// Guardar Alcance
function guardar_alcance() {
    alcance = JSON.stringify(alcanceQuill.getContents());
    $('#alcance').val(alcance);
}

// Llenar Alcance
function llenar_alcance(contenido) {
    alcanceQuill.setContents(contenido);
}

// Guardar Documentos
function guardar_documentos() {
    documentos = JSON.stringify(documentosQuill.getContents());
    $('#documentos').val(documentos);
}

// Llenar Documentos
function llenar_documentos(contenido) {
    documentosQuill.setContents(contenido);
}

// Guardar Definiciones
function guardar_definiciones() {
    definiciones = JSON.stringify(definicionesQuill.getContents());
    $('#definiciones').val(definiciones);
}

// Llenar Definiciones
function llenar_definiciones(contenido) {
    definicionesQuill.setContents(contenido);
}

// Guardar Responsabilidades
function guardar_responsabilidades() {
    responsabilidades = JSON.stringify(responsabilidadesQuill.getContents());
    $('#responsabilidades').val(responsabilidades);
}

// Llenar Responsabilidades
function llenar_responsabilidades(contenido) {
    responsabilidadesQuill.setContents(contenido);
}

// Guardar Desarrollo
function guardar_desarrollo() {
    desarrollo = JSON.stringify(desarrolloQuill.getContents());
    $('#desarrollo').val(desarrollo);
}

// Llenar Desarrollo
function llenar_desarrollo(contenido) {
    desarrolloQuill.setContents(contenido);
}

// Guardar Registros
function guardar_registros() {
    var tabla = $('#registro_dataTable1').DataTable();
    var registros = JSON.parse(JSON.stringify("{}"));
    let datos = tabla.rows().data();
    if (datos.length > 0) {
        registros = JSON.stringify(tabla.data()).split(',"context":')[0] + "}";
    }
    $('#registros').val(registros);
}

// Guardar Control de Cambios
function guardar_control_cambios() {
    var tabla_control = $('#cambio_dataTable1').DataTable();
    var control_cambios = JSON.parse(JSON.stringify("{}"));
    let datos = tabla_control.rows().data();
    if (datos.length > 0) {
        control_cambios = JSON.stringify(tabla_control.data()).split(',"context":')[0] + "}";
    }
    $('#control_cambios').val(control_cambios);
}

// Guardar Autorizaciones
function guardar_autorizaciones() {
    autorizaciones = $('#autorizaciones').val();
    console.log('OK Todo bien');
}

// STEPS

// DOM elements
const DOMstrings = {
    stepsBtnClass: 'multisteps-form__progress-btn',
    stepsBtns: document.querySelectorAll(`.multisteps-form__progress-btn`),
    stepsBar: document.querySelector('.multisteps-form__progress'),
    stepsForm: document.querySelector('.multisteps-form__form'),
    stepsFormTextareas: document.querySelectorAll('.multisteps-form__textarea'),
    stepFormPanelClass: 'multisteps-form__panel',
    stepFormPanels: document.querySelectorAll('.multisteps-form__panel'),
    stepPrevBtnClass: 'js-btn-prev',
    stepNextBtnClass: 'js-btn-next',
    stepSaveBtnClass: 'js-btn-save'
};

// remove class from a set of items
const removeClasses = (elemSet, className) => {
    elemSet.forEach(elem => {
        elem.classList.remove(className);
    });
};

// return exect parent node of the element
const findParent = (elem, parentClass) => {
    let currentNode = elem;
    while (!currentNode.classList.contains(parentClass)) {
        currentNode = currentNode.parentNode;
    }
    return currentNode;
};

// get active button step number
const getActiveStep = elem => {
    return Array.from(DOMstrings.stepsBtns).indexOf(elem);
};

// set all steps before clicked (and clicked too) to active
const setActiveStep = activeStepNum => {
    // remove active state from all the state
    removeClasses(DOMstrings.stepsBtns, 'js-active');
    // set picked items to active
    DOMstrings.stepsBtns.forEach((elem, index) => {
        if (index <= activeStepNum) {
            elem.classList.add('js-active');
        }
    });
};

// get active panel
const getActivePanel = () => {
    let activePanel;
    DOMstrings.stepFormPanels.forEach(elem => {
        if (elem.classList.contains('js-active')) {
            activePanel = elem;
        }
    });
    return activePanel;
};

// open active panel (and close unactive panels)
const setActivePanel = activePanelNum => {
    // remove active class from all the panels
    removeClasses(DOMstrings.stepFormPanels, 'js-active');
    // show active panel
    DOMstrings.stepFormPanels.forEach((elem, index) => {
        if (index === activePanelNum) {
            elem.classList.add('js-active');
            setFormHeight(elem);
        }
    });
};

// set form height equal to current panel height
const formHeight = activePanel => {
    const activePanelHeight = activePanel.offsetHeight;
    DOMstrings.stepsForm.style.height = `${activePanelHeight}px`;
};

const setFormHeight = () => {
    const activePanel = getActivePanel();
    formHeight(activePanel);
};

// STEPS BAR CLICK FUNCTION
DOMstrings.stepsBar.addEventListener('click', e => {
    // check if click target is a step button
    const eventTarget = e.target;
    if (!eventTarget.classList.contains(`${DOMstrings.stepsBtnClass}`)) {
        return;
    }
    // get active button step number
    const activeStep = getActiveStep(eventTarget);
    // set all steps before clicked (and clicked too) to active
    setActiveStep(activeStep);
    // open active panel
    setActivePanel(activeStep);
});

// PREV/NEXT BTNS CLICK
DOMstrings.stepsForm.addEventListener('click', e => {
    const eventTarget = e.target;
    // check if we clicked on `PREV` or NEXT`  buttons
    if (!(eventTarget.classList.contains(`${DOMstrings.stepPrevBtnClass}`) || eventTarget.classList.contains(`${DOMstrings.stepNextBtnClass}`))) {
        return;
    }
    // find active panel
    const activePanel = findParent(eventTarget, `${DOMstrings.stepFormPanelClass}`);
    let activePanelNum = Array.from(DOMstrings.stepFormPanels).indexOf(activePanel);
    // set active step and active panel onclick
    if (eventTarget.classList.contains(`${DOMstrings.stepPrevBtnClass}`)) {
        activePanelNum--;
    } else {
        activePanelNum++;
    }
    setActiveStep(activePanelNum);
    setActivePanel(activePanelNum);
});

// SETTING PROPER FORM HEIGHT ONLOAD
window.addEventListener('load', setFormHeight, false);

// SETTING PROPER FORM HEIGHT ONRESIZE
window.addEventListener('resize', setFormHeight, false);
