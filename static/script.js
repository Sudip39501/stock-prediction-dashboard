// Load stocks data for the landing page
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing application");
    
    // Check if we're on the index page or stock detail page
    if (document.getElementById('stocksGrid')) {
        console.log("Loading stocks for landing page");
        loadStocks();
    }
    
    if (document.getElementById('priceChart')) {
        console.log("Initializing stock detail page");
        initializeStockPage();
    }
});

// Load and display stock cards
async function loadStocks() {
    const stocksGrid = document.getElementById('stocksGrid');
    const loading = document.getElementById('loading');
    
    console.log("Starting to load stocks...");
    
    try {
        // First test if API is reachable
        console.log("Testing API connection...");
        const testResponse = await fetch('/test');
        if (!testResponse.ok) {
            throw new Error('API server is not responding');
        }
        const testData = await testResponse.json();
        console.log("API test passed:", testData);
        
        // Now fetch stocks data
        console.log("Fetching stocks data from /stocks endpoint");
        const response = await fetch('/stocks');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stocks = await response.json();
        console.log("Stocks data received:", stocks);
        
        loading.style.display = 'none';
        
        if (stocks.length === 0) {
            stocksGrid.innerHTML = `
                <div class="error" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                    <h3>No stock data available</h3>
                    <p>This might be due to network issues or API limitations.</p>
                    <p>Please check your internet connection and try again.</p>
                    <button onclick="loadStocks()" class="predict-btn" style="margin-top: 15px;">
                        Try Again
                    </button>
                </div>
            `;
            return;
        }
        
        // Clear existing content
        stocksGrid.innerHTML = '';
        
        stocks.forEach(stock => {
            const stockCard = createStockCard(stock);
            stocksGrid.appendChild(stockCard);
        });
        
        console.log("Stock cards created successfully");
        
    } catch (error) {
        console.error('Error loading stocks:', error);
        loading.innerHTML = `
            <div class="error" style="text-align: center; padding: 40px;">
                <h3>Connection Error</h3>
                <p>Error: ${error.message}</p>
                <p>Make sure the Flask server is running on port 5000.</p>
                <button onclick="loadStocks()" class="predict-btn" style="margin-top: 15px;">
                    Try Again
                </button>
                <div style="margin-top: 20px; font-size: 0.9em; color: #666;">
                    <p>If this continues, check:</p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Flask server is running</li>
                        <li>No other apps using port 5000</li>
                        <li>You have internet connection</li>
                    </ul>
                </div>
            </div>
        `;
    }
}

// Create a stock card element
function createStockCard(stock) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.onclick = () => {
        console.log(`Navigating to stock detail: ${stock.symbol}`);
        window.location.href = `/stock/${stock.symbol}`;
    };
    
    const returnClass = stock.avg_daily_return >= 0 ? 'positive' : 'negative';
    const returnSign = stock.avg_daily_return >= 0 ? '+' : '';
    
    card.innerHTML = `
        <div class="stock-symbol">${stock.symbol}</div>
        <div class="stock-name">${stock.name}</div>
        <div class="stock-price">$${stock.price}</div>
        <div class="stock-return ${returnClass}">
            ${returnSign}${stock.avg_daily_return}%
        </div>
    `;
    
    return card;
}

// Initialize the stock detail page
function initializeStockPage() {
    console.log("Initializing stock page for:", symbol);
    
    // Set up chart period buttons
    const chartButtons = document.querySelectorAll('.chart-btn');
    chartButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            chartButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Load chart data for selected period
            loadChartData(this.dataset.period);
        });
    });
    
    // Set up prediction button
    const predictBtn = document.getElementById('predictBtn');
    if (predictBtn) {
        predictBtn.addEventListener('click', predictStock);
    }
    
    // Load initial chart data (3 months)
    loadChartData('3m');
}

// Load and display chart data
async function loadChartData(period) {
    console.log(`Loading chart data for period: ${period}`);
    
    const chartContainer = document.getElementById('priceChart').parentElement;
    
    try {
        chartContainer.innerHTML = '<div class="loading">Loading chart data...</div>';
        
        const response = await fetch(`/stock/${symbol}/history`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        console.log(`Chart data loaded for ${period}:`, data[period].length, "data points");
        
        chartContainer.innerHTML = '<canvas id="priceChart"></canvas>';
        renderPriceChart(data[period], period);
        
    } catch (error) {
        console.error('Error loading chart data:', error);
        chartContainer.innerHTML = `
            <div class="error">
                Error loading chart data: ${error.message}
                <button onclick="loadChartData('${period}')" style="margin-left: 10px; padding: 5px 10px;">
                    Retry
                </button>
            </div>
        `;
    }
}

// Render the price chart using Chart.js
function renderPriceChart(chartData, period) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.priceChart instanceof Chart) {
        window.priceChart.destroy();
    }
    
    const labels = chartData.map(item => {
        // Format date to be more readable
        const date = new Date(item.date);
        return date.toLocaleDateString();
    });
    
    const prices = chartData.map(item => item.price);
    
    const chartTitle = `${symbol} Stock Price (${period})`;
    
    window.priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: chartTitle,
                data: prices,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

// Predict stock prices
async function predictStock() {
    const predictBtn = document.getElementById('predictBtn');
    const resultsDiv = document.getElementById('predictionResults');
    
    predictBtn.disabled = true;
    predictBtn.textContent = 'Predicting...';
    resultsDiv.innerHTML = '<div class="loading">Generating predictions using AI... This may take a moment.</div>';
    
    try {
        const response = await fetch(`/stock/${symbol}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayPredictionResults(data);
        
    } catch (error) {
        console.error('Prediction error:', error);
        resultsDiv.innerHTML = `
            <div class="error">
                Error generating predictions: ${error.message}
                <button onclick="predictStock()" style="margin-left: 10px; padding: 5px 10px;">
                    Try Again
                </button>
            </div>
        `;
    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Predict Future Prices';
    }
}

// Display prediction results
function displayPredictionResults(data) {
    const resultsDiv = document.getElementById('predictionResults');
    
    resultsDiv.innerHTML = `
        <h3>30-Day Price Prediction</h3>
        <div class="prediction-chart-container">
            <canvas id="predictionChart"></canvas>
        </div>
        <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <h4>Next 5 Days:</h4>
            <ul>
                ${data.future_dates.slice(0, 5).map((date, i) => 
                    `<li><strong>${date}:</strong> $${data.future_prices[i].toFixed(2)}</li>`
                ).join('')}
            </ul>
        </div>
    `;
    
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.future_dates,
            datasets: [{
                label: 'Predicted Price',
                data: data.future_prices,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                }
            }
        }
    });
}