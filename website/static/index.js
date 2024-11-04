function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const dataTableBody = document.getElementById('data-table-body');
            dataTableBody.innerHTML = '';  // Clear the current table data

            if (Object.keys(data).length > 0) {
                for (const [key, value] of Object.entries(data)) {
                    const row = document.createElement('tr');
                    row.innerHTML = `<td>${key}</td><td>${value}</td>`;
                    dataTableBody.appendChild(row);
                }
            } else {
                dataTableBody.innerHTML = '<tr><td colspan="2">No data available.</td></tr>';
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Fetch data every 5 seconds
setInterval(fetchData, 5000);  // Adjust the interval as needed
