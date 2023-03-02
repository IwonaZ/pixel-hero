const imageForm = document.getElementsByClassName("image-form");
const mainForm = document.querySelector("#pictures_container_form");
const addImageFormBtn = document.querySelector("#add-image-form");
const submitFormBtn = document.querySelector('[type="submit"]');
const totalForms = document.querySelector("#id_form-TOTAL_FORMS");

let formCount = imageForm.length - 1;

function updateForms() {
    let count = 0;
    for (let form of imageForm) {
        const labels = form.querySelectorAll("label")
        const inputs = form.querySelectorAll("input")
        labels[0].setAttribute("for",`id_form-${count}-image`)
        labels[1].setAttribute("for",`id_form-${count}-gallery`)
        inputs[0].setAttribute("name", `form-${count}-image`)
        inputs[0].setAttribute("id", `id_form-${count}-image`)
        count++
        }
        // const formRegex = RegExp(`form-(\\d){1}-`, 'g');
        // form.innerHTML = form.innerHTML.replace(formRegex, `form-${count++}-`)
    
}

addImageFormBtn.addEventListener("click", function (event) {
    event.preventDefault();

    const newImageForm = imageForm[0].cloneNode(true);
    const formRegex = RegExp(`form-(\\d){1}-`, 'g');

    formCount++;

    newImageForm.innerHTML = newImageForm.innerHTML.replace(formRegex, `form-${formCount}-`);
    mainForm.insertBefore(newImageForm, submitFormBtn);
    totalForms.setAttribute('value', `${formCount + 1}`);
});

mainForm.addEventListener("click", function (event) {
    if (event.target.classList.contains("delete-image-form")) {
        event.preventDefault();
        // Prevent deleting form if only one available. 
        if (!formCount) {
            return
        }
        event.target.parentElement.remove();
        formCount--;
        updateForms();
        totalForms.setAttribute('value', `${formCount + 1}`);
    }
});