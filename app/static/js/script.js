// Função para exibir a mensagem flutuante
function showToast() {
    var toast = document.getElementById("toast");
    toast.classList.add("show");
    setTimeout(function(){ toast.classList.remove("show"); }, 3000);
}

// Exibir a mensagem flutuante se houver mensagens flash
window.onload = function() {
    var toast = document.getElementById("toast");
    if (toast) {
        showToast();
    }
};
