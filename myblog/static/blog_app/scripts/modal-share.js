// Share post modal
var modal_share = document.getElementById("modal-share")
var btn_share = document.getElementById("modal-share-btn")
var close_share = document.getElementById("close-share")

// Open modal on click button
btn_share.onclick = function () {
    modal_share.style.display = "block";
}
// Close modal on click button
close_share.onclick = function () {
    modal_share.style.display = "none";
}