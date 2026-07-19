/** @odoo-module **/

//___FORMULAIRE INSTALLATEUR___________________________________________________

const installerPage = document.querySelector("#installer_page");

if (!installerPage) {
    return;
}

//___TVA___
const vatSubject = document.getElementById("vat_subject");
const vatContainer = document.getElementById("vat_container");
const vatInput = document.getElementById("vat");

if (vatSubject && vatContainer && vatInput) {

    function toggleVat() {
        if (vatSubject.checked) {
            vatContainer.classList.remove("d-none");
            vatInput.required = true;
        } else {
            vatContainer.classList.add("d-none");
            vatInput.required = false;
            vatInput.value = "";
        }
    }

    vatSubject.addEventListener("change", toggleVat);

    toggleVat();
}

//___HORAIRES D'OUVERTURE___
const container = document.getElementById("opening_infos");
if (!container) return;

const checkboxes = container.querySelectorAll("input[type='checkbox']");

let firstInvalidDay = null;

// Dévérouillage des champs
function toggleDayInputs(cb) {

    const dayContainer = cb.closest(".d-flex.flex-row").nextElementSibling.nextElementSibling;

    const inputs = dayContainer.querySelectorAll("input[type='time']");

    inputs.forEach(input => {
        input.disabled = !cb.checked;
    });
}

// Validation des horaires
function validateOpeningHours(changedInput = null) {

    let invalidDays = false;
    let firstInvalidDay = null;
    let atLeastOneDayIsOk = false;
    let openningHoursAlert = document.querySelector('#openning-hours-alert');

    const checkboxes = container.querySelectorAll("input[type='checkbox']");

    checkboxes.forEach(cb => {

        const alertMessage = cb.parentElement.parentElement.nextElementSibling;
        const day = cb.name.replace("_openned", "");
        const openMorning = container.querySelector(`[name='${day}_morning_open']`);
        const closeMorning = container.querySelector(`[name='${day}_morning_close']`);
        const openAfternoon = container.querySelector(`[name='${day}_afternoon_open']`);
        const closeAfternoon = container.querySelector(`[name='${day}_afternoon_close']`);

        // Reset si décoché
        if (!cb.checked) {
            alertMessage.innerHTML = "";
            openMorning.value = "";
            closeMorning.value = "";
            openAfternoon.value = "";
            closeAfternoon.value = "";
            return;
        }

        // Nettoyage des horaires partiellement saisies (Exemple: 12:--)
        const timeInputs = [
            openMorning,
            closeMorning,
            openAfternoon,
            closeAfternoon
        ];

        timeInputs.forEach(input => {
            if (input && !input.checkValidity()) {
                input.value = "";
            }
        });

        // Vérification des horaires non saisis
        let incoherentHoursMessage = null;
        const continuousOpeningHours = Boolean(
            openMorning.value &&
            !closeMorning.value &&
            !openAfternoon.value &&
            closeAfternoon.value
        )

        if (!continuousOpeningHours) {
            if (!openMorning.value && closeMorning.value) {
                incoherentHoursMessage = "(Veuillez saisir l'heure d'ouverture le matin)";
            } else if (openMorning.value && !closeMorning.value) {
                incoherentHoursMessage = "(Veuillez saisir l'heure de fermeture le matin)";
            } else if (!openAfternoon.value && closeAfternoon.value) {
                incoherentHoursMessage = "(Veuillez saisir l'heure d'ouverture l'après-midi)";
            } else if (openAfternoon.value && !closeAfternoon.value) {
                incoherentHoursMessage = "(Veuillez saisir l'heure de fermeture l'après-midi)";
            }
        }

        // Vérification cohérence des horaires saisis
        // Matin
        if (openMorning.value && closeMorning.value) {
            if (!isHourRangeValid(openMorning, closeMorning)) {
                incoherentHoursMessage = "(L'heure de fermeture du matin doit être postérieure à l'heure d'ouverture)";
            }
        }
        // Après-midi
        if (openAfternoon.value && closeAfternoon.value) {
            if (!isHourRangeValid(openAfternoon, closeAfternoon)) {
                incoherentHoursMessage = "(L'heure de fermeture de l'après-midi doit être postérieure à l'heure de réouverture)";
            }
        }
        // Après-midi > matin
        if (openMorning.value && closeMorning.value && openAfternoon.value && closeAfternoon.value) {
            if (!isHourRangeValid(closeMorning, openAfternoon)) {
                incoherentHoursMessage = "(L'heure de réouverture l'après-midi doit être postérieure à l'heure de fermeture du matin)";
            }
        }
        // Journée continue
        if (openMorning.value && closeAfternoon.value) {
            if (!isHourRangeValid(openMorning, closeAfternoon)) {
                incoherentHoursMessage = "(L'heure de fermeture de l'après-midi doit être postérieure à l'heure d'ouverture)";
            }
        }

        // Vérification de la définition des horaires requis si jour coché
        const invalid = !openMorning || !closeAfternoon || !openMorning.value || !closeAfternoon.value;

        // Champs valides ?
        if (invalid || incoherentHoursMessage) {

            invalidDays = true;

            // Message d'erreur pour un jour
            let message = "";

            if (incoherentHoursMessage) {
                message = incoherentHoursMessage;
            } else {
                message = "(Vous devez remplir au minimum l'heure d'ouverture et de fermeture)"
            }

            alertMessage.innerHTML = `<span class='small text-danger'> ${message}</span>`;

            // Premier jour invalide
            if (!firstInvalidDay) {
                firstInvalidDay = day;  // => scroll auto
            }

        } else {
            atLeastOneDayIsOk = true;

            if (alertMessage.innerHTML != "") {
                alertMessage.innerHTML = "";
            }
        }
    })

    // Message d'erreur général
    if (!atLeastOneDayIsOk) {
        openningHoursAlert.innerHTML = "<div class='small text-danger'> (Vous devez remplir au minimum un jour d'ouverture)</div>";
    } else {
        openningHoursAlert.innerHTML = "";
    }

    return {
        invalidDays,
        firstInvalidDay,
        atLeastOneDayIsOk
    }
}

// Fonction vérifiant la cohérence des horaires définis
function isHourRangeValid(open, close) {

    if (!open.value || !close.value) {
        return false;
    }

    const [openHour, openMinute] = open.value.split(":").map(Number);
    const [closeHour, closeMinute] = close.value.split(":").map(Number);

    const openTotal = openHour * 60 + openMinute;
    const closeTotal = closeHour * 60 + closeMinute;

    return closeTotal > openTotal;
}

// Ecouteurs d'évènements
checkboxes.forEach(cb => {
    cb.addEventListener("change", function () {
        toggleDayInputs(this);
        validateOpeningHours();
    });
});

container.querySelectorAll("input[type='time']").forEach(input => {
    input.addEventListener("blur", function () {
        validateOpeningHours(this);
    })

})

installerPage.querySelector("form").addEventListener("submit", function (e) {

    const result = validateOpeningHours();

    if (!result.atLeastOneDayIsOk || result.invalidDays) {

        // Bloquage du formulaire
        e.preventDefault();

        // Elément invalide vers lequel le scroll va aller
        let el = null;

        if (!result.atLeastOneDayIsOk) {
            el = container.firstElementChild;
        } else if (result.firstInvalidDay) {
            el = container.querySelector(`[name='${result.firstInvalidDay}']`);
        }

        // Scroll auto
        if (el) {
            el.scrollIntoView({
                behavior: "smooth",
                block: "center"
            })
        }
    }
})