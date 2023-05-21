function showHideDiv(id) {
    var e = document.getElementById(id);
    if(e.style.display == null || e.style.display == "none") {
        e.style.display = "table-row";
    } else {
        e.style.display = "none";
    }
}