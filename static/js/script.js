document.addEventListener('DOMContentLoaded', (event) => {
    searchTicker('{{ default_ticker }}'); // Load the default ticker data on page load
});

function searchTicker(ticker = null) {
    if (!ticker) {
        ticker = document.getElementById('ticker').value;
    } else {
        document.getElementById('ticker').value = ticker; // Update the search bar with the clicked ticker
    }
    fetch('/search_ticker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: ticker })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Chart data:', data.chart_data);
            updateChart(data.chart_data);
            document.getElementById('open').innerText = data.current_price.open;
            document.getElementById('high').innerText = data.current_price.high;
            document.getElementById('low').innerText = data.current_price.low;
            document.getElementById('close').innerText = data.current_price.close;
            document.getElementById('predicted').innerText = data.predicted_price;
        })
        .catch(error => console.error('Error:', error));
}

function updateChart(data) {
    console.log('Updating chart with data:', data);

    const trace1 = {
        x: data.x,
        close: data.close,
        decreasing: { line: { color: 'red' } },
        high: data.high,
        increasing: { line: { color: 'green' } },
        low: data.low,
        open: data.open,
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y'
    };

    const layout = {
        title: 'Stock Price Data',
        xaxis: {
            title: 'Date'
        },
        yaxis: {
            title: 'Price'
        }
    };

    const chartData = [trace1];
    Plotly.newPlot('chart', chartData, layout);
}

function addToWishlist() {
    const ticker = document.getElementById('ticker').value;
    fetch('/add_to_wishlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: ticker })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const wishlist = document.getElementById('wishlist');
                const newItem = document.createElement('li');
                newItem.innerText = ticker;
                newItem.setAttribute('data-ticker', ticker);
                newItem.onclick = () => searchTicker(ticker);
                wishlist.appendChild(newItem);
            }
        })
        .catch(error => console.error('Error:', error));
}
    