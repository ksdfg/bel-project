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