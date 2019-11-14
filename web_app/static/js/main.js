function phoneValidate() {
    if (!Number.isInteger(Number(document.getElementById('number').value)) ||
        document.getElementById('number').value === '') {
        document.getElementById('message-content').innerHTML = 'Invalid Contact Number';
        document.getElementById('message-display').style.display = 'Block'
    }
}

function emailValidate() {
    if (!document.getElementById('email').value.match('.+@.+\\..+')) {
        document.getElementById('message-content').innerHTML = 'Invalid E-Mail ID';
        document.getElementById('message-display').style.display = 'Block'
    }
}

function showMessage() {
    document.getElementById('message-display').style.display = 'block'
}