// Publish post modal
var modal_post = document.getElementById("modal-post")
var btn_post = document.getElementById("modal-post-btn")
var close_post = document.getElementById("close-post")

// Open modal on click button
btn_post.onclick = function () {
    modal_post.style.display = "block";
}
// Close modal on click button
close_post.onclick = function () {
    modal_post.style.display = "none";
}