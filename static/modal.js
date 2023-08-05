document.addEventListener("DOMContentLoaded", function() {
  console.log("loaded");

  document.body.addEventListener("click", function(event) {
    if (event.target.classList.contains("btnMore")) {
      console.log("finded3");
      var uuid = event.target.getAttribute("data-uuid");
      fetchModalData(uuid);
    }
  });
});

function initializeModal(data) {
  var modal = document.getElementById("myModal");
  var modalData = document.getElementById("modalData");
  var span = document.getElementsByClassName("close")[0];



  modalData.innerHTML = data;
  modal.style.display = "block";


  span.onclick = function() {
    modal.style.display = "none";
  };

  window.onclick = function(event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };

  document.addEventListener('keydown', function(e) {
    if (e.keyCode === 27) {
      modal.style.display = 'none';
    }
  });

}

function fetchModalData(uuid) {
  var apiUrl = "http://127.0.0.1:8000/api/cycles?uuid=" + uuid;
  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      console.log("Fetched Data:", data); // Debugging: Check the data received from the API
      if (Array.isArray(data) && data.length > 0) {
        const routeData = data[0]; // Access the first object in the array
        // Process the data from the API
        var modalData = `
          <h2>Маршрут ${routeData.uuid}</h2>
          <p>Вес: ${routeData.weight}</p>
          <p>Длина: ${routeData.length}</p>
          <p>Тип края: ${routeData.edge_type}</p>
          <p>Маршрут: ${routeData.cycle}</p>
          <p>Начальная дата: ${routeData.start_date}</p>
          <p>Конечная дата: ${routeData.end_date}</p>
          <p>Город отправления: ${routeData.cityfrom}</p>
          <p>Город прибытия: ${routeData.cityto}</p>
        `;
        initializeModal(modalData);
      } else {
        console.error("Data not found or invalid format:", data);
      }
    })
    .catch(error => {
      console.error("Error fetching data from API:", error);
    });
}

