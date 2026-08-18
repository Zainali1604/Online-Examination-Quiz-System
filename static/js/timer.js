/**
 * JavaScript Countdown Timer for Online Examination System
 */
function initExamTimer(durationInSeconds, displayElementId, formElementId) {
    let remainingTime = parseInt(durationInSeconds, 10);
    const displayElement = document.getElementById(displayElementId);
    const formElement = document.getElementById(formElementId);

    if (!displayElement) return;

    function updateDisplay() {
        if (remainingTime <= 0) {
            displayElement.innerHTML = "<span class='text-danger fw-bold'>00:00 - Time Expired!</span>";
            if (formElement) {
                // Prevent multiple submissions
                formElement.setAttribute('data-submitting', 'true');
                formElement.submit();
            }
            return;
        }

        const hours = Math.floor(remainingTime / 3600);
        const minutes = Math.floor((remainingTime % 3600) / 60);
        const seconds = remainingTime % 60;

        let timeString = "";
        if (hours > 0) {
            timeString += (hours < 10 ? "0" + hours : hours) + ":";
        }
        timeString += (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);

        displayElement.textContent = timeString;

        // Visual warning when time is less than 2 minutes (120s)
        if (remainingTime <= 120) {
            displayElement.classList.add('text-danger', 'fw-bold');
            displayElement.classList.remove('text-primary', 'text-dark');
        }

        remainingTime--;
    }

    // Initial render
    updateDisplay();

    // Start 1-second interval
    const timerInterval = setInterval(function () {
        if (remainingTime < 0) {
            clearInterval(timerInterval);
        } else {
            updateDisplay();
        }
    }, 1000);
}
