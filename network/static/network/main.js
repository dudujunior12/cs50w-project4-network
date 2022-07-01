// Edit


// Like

document.addEventListener('DOMContentLoaded', () => {
    btn_edit = document.querySelectorAll('#btn-edit').forEach(button => {
        button.onclick = () => {
            let textarea = document.createElement("textarea");
            let div = document.querySelector(".edit");
            div.append(textarea);
        };
    });
});