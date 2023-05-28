// Define an object with options for formatting the date and time
let options = {
  year: 'numeric',
  month: 'numeric',
  day: 'numeric',
  hourCycle: 'h23',
  hour: 'numeric',
  minute: 'numeric',
  second: 'numeric'
};

// Define a function that takes an array of readings and an index as parameters
function html_data_binding(readings) {
  // Use jQuery to update the HTML elements with the corresponding values from the readings array
  for (let reading of readings) {
    if (reading.trans_id == "Xmter-5") {
      $("#bv-5").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-7") {
      $("#bv-7").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-14") {
      $("#bv-14").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-16") {
      $("#bv-16").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-18") {
      $("#bv-18").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-20A") {
      $("#bv-20A").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-20B") {
      $("#bv-20B").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-22A") {
      $("#bv-22A").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-22B") {
      $("#bv-22B").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-25") {
      $("#bv-25").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-31") {
      $("#bv-31").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-34") {
      $("#bv-34").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-37") {
      $("#bv-37").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-39") {
      $("#bv-39").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-40") {
      $("#bv-40").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-41") {
      $("#bv-41").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-42") {
      $("#bv-42").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-43") {
      $("#bv-43").html(`${reading.temp_1.toFixed(2)}`);
    }
    if (reading.trans_id == "Xmter-46") {
      $("#bv-46").html(`${reading.temp_1.toFixed(2)}`);
    }
  }
};
function html_header_binding(nodes) {
  let master_node;
  if (nodes.master_list.length >= 1) {
    master_node = nodes.master_list.find(node => node.power == 0);
  };
  $("#base-master").html(`${master_node.hostname}`);
  $("#online-xmter").html(`${nodes.transmitter_list.length}/19`);
  $("#online-master").html(`${nodes.master_list.length}/5`);
  $("#web-server").html(`${nodes.interface_list.length}/2`);
  $("#data-server").html(`${nodes.data_server_list.length}/3`);
  $("#main-pc").html(`${nodes.maintenance_pc_list.length}/2`);
}

// Define a function that gets data from the server
function get_data_from_server() {
  // Send an AJAX GET request to the Flask view function
  $.ajax({
    type: "GET",
    url: "http://127.0.0.1:60501/internal-reading-list",
    success: function(data) {
      $("#power-level").html(`Power level: ${data.node["power"]}`);
      // Use a loop to call the html_data_binding function for each reading in the array
      html_data_binding(data.readings);
      html_header_binding(data.nodes);
    }
  });
}

// Set the interval in milliseconds
const interval = 5000;

// Call the get_data_from_server function once
get_data_from_server();

// Call the get_data_from_server function every interval milliseconds
setInterval(get_data_from_server, interval);