document.addEventListener('DOMContentLoaded', function() {
  const table = document.getElementById("tableBox");

  // Создание заголовков столбцов таблицы
  const headers = ["Вес", "Длина", "Маршрут", "Тип загрузки", "Начальная дата", "Конечная дата"];
  const headerRow = document.createElement("tr");

  for (let header of headers) {
    const th = document.createElement("th");
    th.textContent = header;
    headerRow.appendChild(th);
  }

  table.appendChild(headerRow);

  // Чтение данных из API
  fetch("http://127.0.0.1:8000/cycles")
      .then(response => response.json())
      .then(data => {
        // Создание строк таблицы
        for (let item of data) {
          const row = document.createElement("tr");

          // Ширина
          const widthCell = document.createElement("td");
          widthCell.textContent = item.weight;
          row.appendChild(widthCell);

          // Длина
          const lenCell = document.createElement("td");
          lenCell.textContent = item.len;
          row.appendChild(lenCell);

          // Маршрут
          const cycleCell = document.createElement("td");
          cycleCell.textContent = item.cycle.join(", ");
          row.appendChild(cycleCell);

          // Тип края
          const edgeTypeCell = document.createElement("td");
          edgeTypeCell.textContent = item.edge_type;
          row.appendChild(edgeTypeCell);

          // Начальная дата
          const startDateCell = document.createElement("td");
          startDateCell.textContent = item.start_date;
          row.appendChild(startDateCell);

          // Конечная дата
          const endDateCell = document.createElement("td");
          endDateCell.textContent = item.end_date;
          row.appendChild(endDateCell);

          table.appendChild(row);
        }
      })
      .catch(error => console.error(error));
});
