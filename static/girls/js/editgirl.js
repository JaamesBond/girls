    document.getElementById('editgirlForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission behavior

        var idValue = document.getElementById('id').value;
        window.location.href = '/editgirl/' + encodeURIComponent(idValue); // Redirect to the constructed URL
    });