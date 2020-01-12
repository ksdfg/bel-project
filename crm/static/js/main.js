function phoneValidate(tagname) {
    if (!Number.isInteger(Number(document.getElementById(tagname.toString()).value)) ||
        document.getElementById('number').value === '') {
        document.getElementById('message-title').innerHTML = 'Error';
        document.getElementById('message-header').className = "w3-container w3-red w3-center";
        document.getElementById('message-content').innerHTML = 'Invalid Contact Number';
        document.getElementById('message-display').style.display = 'Block'
    }
}

function emailValidate(tagname) {
    if (!document.getElementById(tagname).value.match('.+@.+\\..+')) {
        document.getElementById('message-title').innerHTML = 'Error';
        document.getElementById('message-header').className = "w3-container w3-red w3-center";
        document.getElementById('message-content').innerHTML = 'Invalid E-Mail ID';
        document.getElementById('message-display').style.display = 'Block'
    }
}

function showMessage() {
    document.getElementById('message-display').style.display = 'block'
}

// code to ensure user is logged out if he is inactive for more than 15 minutes

var timeoutID;

function setup() {
    this.addEventListener("mousemove", resetTimer, false);
    this.addEventListener("mousedown", resetTimer, false);
    this.addEventListener("keypress", resetTimer, false);
    this.addEventListener("DOMMouseScroll", resetTimer, false);
    this.addEventListener("mousewheel", resetTimer, false);
    this.addEventListener("touchmove", resetTimer, false);
    this.addEventListener("MSPointerMove", resetTimer, false);

    startTimer();
}

setup();

function startTimer() {
    // wait 15 seconds before calling goInactive
    timeoutID = window.setTimeout(goInactive, 900000);
}

function resetTimer(e) {
    window.clearTimeout(timeoutID);
    startTimer()
}

function goInactive() {
    window.location.href = '/logout'    // logout the user
}