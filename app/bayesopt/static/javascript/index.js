var activeDropdown = {};
document = document.open('../../templates/index.html');
document.getElementById('parameter-dropdown').addEventListener('click',showDropdown);
function showDropdown(event){
    Logger.log("linked")
    if (activeDropdown.id && activeDropdown.id !== event.target.id) {
    activeDropdown.element.classList.remove('active');
    }
    //checking if a list element was clicked, changing the inner button value
    if (event.target.tagName === 'LI') {
    activeDropdown.button.innerHTML = event.target.innerHTML;
    for (var i=0;i<event.target.parentNode.children.length;i++){
    if (event.target.parentNode.children[i].classList.contains('check')) {
    event.target.parentNode.children[i].classList.remove('check');
    }
    }
    //timeout here so the check is only visible after opening the dropdown again
    window.setTimeout(function(){
        event.target.classList.add('check');
    },500)
    }
    for (var i = 0;i<this.children.length;i++){
    if (this.children[i].classList.contains('dropdown-selection')){
    activeDropdown.id = this.id;
    activeDropdown.element = this.children[i];
    this.children[i].classList.add('active');
    }
    //adding the dropdown-button to our object
    else if (this.children[i].classList.contains('dropdown-button')){
    activeDropdown.button = this.children[i];
    }
    }
    }

    window.onclick = function(event) {
    if (!event.target.classList.contains('dropdown-button')) {
    activeDropdown.element.classList.remove('active');
    }
}