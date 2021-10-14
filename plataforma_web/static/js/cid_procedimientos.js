// cid_procedimientos.js

// Guardar Encabezado
function guardar_encabezado() {
    titulo_procedimiento = $('#titulo_procedimiento').val();
    codigo = $('#codigo').val();
    revision = $('#revision').val();
    fecha = $('#fecha').val();
    console.log(titulo_procedimiento);
    console.log(codigo);
    console.log(revision);
    console.log(fecha);
}

// Guardar Objetivo
function guardar_objetivo() {
    objetivo = JSON.stringify(objetivoQuill.getContents());
    $('#objetivo').val(objetivo);
    console.log(objetivo);
}

// Guardar Alcance
function guardar_alcance() {
    alcance = JSON.stringify(alcanceQuill.getContents());
    $('#alcance').val(alcance);
    console.log(alcance)
}

// Guardar Documentos
function guardar_documentos() {
    documentos = JSON.stringify(documentosQuill.getContents());
    $('#documentos').val(documentos);
    console.log(documentos);
}

// Guardar Definiciones
function guardar_definiciones() {
    definiciones = JSON.stringify(definicionesQuill.getContents());
    $('#definiciones').val(definiciones);
    console.log(definiciones);
}

// Guardar Responsabilidades
function guardar_responsabilidades() {
    responsabilidades = JSON.stringify(responsabilidadesQuill.getContents());
    $('#responsabilidades').val(responsabilidades);
    console.log(responsabilidades);
}

// Guardar Desarrollo
function guardar_desarrollo() {
    desarrollo = JSON.stringify(desarrolloQuill.getContents());
    $('#desarrollo').val(desarrollo);
    console.log(desarrollo);
}

// Guardar Registros
function guardar_registros() {
    registros = JSON.stringify(registrosQuill.getContents());
    $('#registros').val(registros);
    console.log(registros);
}

// Guardar Control de Cambios
function guardar_control_cambios() {
    elaboro_nombre = $('#elaboro_nombre').val()
    elaboro_puesto = $('#elaboro_puesto').val()
    elaboro_email = $('#elaboro_email').val()
    console.log(elaboro_nombre, elaboro_puesto, elaboro_email);
    reviso_nombre = $('#reviso_nombre').val()
    reviso_puesto = $('#reviso_puesto').val()
    reviso_email = $('#reviso_email').val()
    console.log(reviso_nombre, reviso_puesto, reviso_email);
    aprobo_nombre = $('#aprobo_nombre').val()
    aprobo_puesto = $('#aprobo_puesto').val()
    aprobo_email = $('#aprobo_email').val()
    console.log(aprobo_nombre, aprobo_puesto, aprobo_email);
    control_cambios = JSON.stringify(controlCambiosQuill.getContents());
    $('#control_cambios').val(control_cambios);
    console.log(control_cambios);
}

// Guardar Vista Previa
function guardar_vista_previa() {
    console.log('OK Vista Previa');
}

// Mostrar Vista Previa
function mostrar_vista_previa() {
    let html = '';
    $('#vista_previa_div').html('');
    let titulo = "<h1><center>" + $('#titulo_procedimiento').val() + "</center></h1>";
    let objetivo = objetivoQuill.root.innerHTML;
    let alcance = alcanceQuill.root.innerHTML;
    let documentos = documentosQuill.root.innerHTML;
    let definiciones = definicionesQuill.root.innerHTML;
    let responsabilidades = responsabilidadesQuill.root.innerHTML;
    let desarrollo = desarrolloQuill.root.innerHTML;
    let registros = registrosQuill.root.innerHTML;
    let control_de_cambios = controlCambiosQuill.root.innerHTML;
    html = titulo + objetivo + alcance + documentos + definiciones + responsabilidades + desarrollo + registros + control_de_cambios;
    document.getElementById('vista_previa_quill').innerHTML = html;
    document.getElementById('vista_previa').innerHTML = html;
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
    stepNextBtnClass: 'js-btn-next'
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
    // mostrar vista previa del procedimiento
    mostrar_vista_previa();
});

// PREV/NEXT BTNS CLICK
DOMstrings.stepsForm.addEventListener('click', e => {
    const eventTarget = e.target;
    // check if we clicked on `PREV` or NEXT` buttons
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
    mostrar_vista_previa();
});

// SETTING PROPER FORM HEIGHT ONLOAD
window.addEventListener('load', setFormHeight, false);

// SETTING PROPER FORM HEIGHT ONRESIZE
window.addEventListener('resize', setFormHeight, false);
