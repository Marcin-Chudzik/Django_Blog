// Comment post modal
const modal_comment = document.getElementById("modal-comment");
const btn_comment = document.getElementById("modal-comment-btn");
const close_comment = document.getElementById("close-comment");

// Open modal on click button
btn_comment.onclick = function () {
    modal_comment.style.display = "block";
}
// Close modal on click button
close_comment.onclick = function () {
    modal_comment.style.display = "none";
}