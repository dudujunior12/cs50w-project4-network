
document.addEventListener("DOMContentLoaded", function() {
// Edit Post
    // When button is clicked open edit form
    document.querySelectorAll('#btn-edit').forEach(button => {
        button.onclick = function(){
            id = this.dataset.id;
            let form = document.querySelector('#form_' + id);
            form.style.display = "block";
            let post = document.querySelector('#post_' + id);
            post.style.display = "none";
            document.querySelector('#txtarea_' + this.dataset.id).value = post.innerHTML;
        }
    });

    // Update user post
    document.querySelectorAll('.form-edit').forEach(form => {
        form.onsubmit = function(event){
            event.preventDefault();

            fetch('/edit-post/' + this.dataset.id, {
                method: 'POST', 
                body: JSON.stringify({
                    post_text: document.querySelector('#txtarea_' + this.dataset.id).value
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                this.style.display = "none";
                document.querySelector('#post_' + id).innerHTML = document.querySelector('#txtarea_' + this.dataset.id).value;
                document.querySelector('#post_' + id).style.display = "block";
            })
            .catch(error => {
                console.log("Error: ", error);
            });

            return false;
        }
    });
});




// Like

