document.getElementById('deleteForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission behavior

    var idValue = document.getElementById('id_del').value;
    window.location.href = '/deletegirl/' + encodeURIComponent(idValue); // Redirect to the constructed URL
});