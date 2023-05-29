

$("#pdfForm").submit(function(event) {
    event.preventDefault(); // prevent the default form submission
    var formData = $(this).serializeArray(); // get the form data as a string
    var jsonData = JSON.stringify({email: formData[0].value}); // convert the array into a JSON string
    $.ajax({
        type: "POST", // specify the request method
        dataType: "json",
        contentType: "application/json",
        url: "http://127.0.0.1:60501/send-email", // specify the request URL
        data: jsonData, // send the form data
        success: function(response) {
            // $("#result").html(response); // display the response in the result div
        }
    });
    this.reset();
});

