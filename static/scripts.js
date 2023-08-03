function showHideDiv(id) {
    var e = document.getElementById(id);
    if(e.style.display == null || e.style.display == "none") {
        e.style.display = "table-row";
    } else {
        e.style.display = "none";
    }
}

//modal dialog
function displayDialog(){
    var button = document.getElementById('open');
    var close = document.getElementById('close');
    var modal = document.getElementById('modal');
    button.addEventListener('click', function (event) {
        event.preventDefault();
        modal.style.display = 'block';
    });
}

function closeDialog(){
    close.addEventListener('click', function (event) {
        event.preventDefault();
        modal.style.display = 'none';
    });
}
