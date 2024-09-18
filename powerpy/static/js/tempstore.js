interact('.item')
.draggable({
inertia: false,
modifiers: [
  interact.modifiers.restrictRect({
    restriction: 'parent',
    endOnly: true
  })
],
autoScroll: true,
listeners: {
  move: dragMoveListener,
}
})
.resizable({
edges: { left: true, right: true, bottom: true, top: true },
listeners: {
  move: resizeMoveListener
},
modifiers: [
  interact.modifiers.restrictEdges({
    outer: 'parent',
    endOnly: true,
  }),
  interact.modifiers.restrictSize({
    min: { width: 100, height: 100 },
  }),
],
inertia: true,
});

function changeItemColor() {
var itemId = document.getElementById('itemSelect').value;
var color = document.getElementById('colorPicker').value;
document.getElementById(itemId).style.backgroundColor = color;
}


function dragMoveListener(event) {
var target = event.target;
var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';

target.setAttribute('data-x', x);
target.setAttribute('data-y', y);
}

function resizeMoveListener(event) {
var target = event.target;
var x = (parseFloat(target.getAttribute('data-x')) || 0);
var y = (parseFloat(target.getAttribute('data-y')) || 0);

target.style.width = event.rect.width + 'px';
target.style.height = event.rect.height + 'px';

x += event.deltaRect.left;
y += event.deltaRect.top;

target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

target.setAttribute('data-x', x);
target.setAttribute('data-y', y);
}

// Add a class while resizing for visual feedback
interact('.item')
.on('resizemove', function (event) {
event.target.classList.add('resizing');
})
.on('resizeend', function (event) {
event.target.classList.remove('resizing');
});






/*
interact('.item')
.on('dragstart', function (event) {
event.target.style.zIndex = 10;
})
.on('dragend', function (event) {
event.target.style.zIndex = 1;
});
*/



function changeItemColor() {
var itemId = document.getElementById('itemSelect').value;
var color = document.getElementById('colorPicker').value;
document.getElementById(itemId).style.backgroundColor = color;
}




let itemCount = 0; // Start with 2 items
let lastClickedItem = null;
function initializeInteract(element) {
interact(element)
    .draggable({
        inertia: true,
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: 'parent',
                endOnly: true
            })
        ],
        autoScroll: true,
        listeners: {
            move: dragMoveListener,
        }
    })
    .resizable({
        edges: { left: true, right: true, bottom: true, top: true },
        listeners: {
            move: resizeMoveListener
        },
        modifiers: [
            interact.modifiers.restrictEdges({
                outer: 'parent',
                endOnly: true,
            }),
            interact.modifiers.restrictSize({
                min: { width: 100, height: 100 },
            }),
        ],
        inertia: true,
    })
    .on('resizemove', function (event) {
        event.target.classList.add('resizing');
    })
    .on('resizeend', function (event) {
        event.target.classList.remove('resizing');
    });
}


function resizeMoveListener(event) {
var target = event.target;
var x = (parseFloat(target.getAttribute('data-x')) || 0);
var y = (parseFloat(target.getAttribute('data-y')) || 0);

target.style.width = event.rect.width + 'px';
target.style.height = event.rect.height + 'px';

x += event.deltaRect.left;
y += event.deltaRect.top;

target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

target.setAttribute('data-x', x);
target.setAttribute('data-y', y);
}

function addNewItem() {
itemCount++;
var newItem = document.createElement('div');
newItem.className = 'item';
newItem.id = 'item' + itemCount;
newItem.textContent = 'Item ' + itemCount;
document.getElementById('container').appendChild(newItem);
initializeInteract(newItem);
updateItemSelect();
}

function updateItemSelect() {
var select = document.getElementById('itemSelect');
select.innerHTML = '';
document.querySelectorAll('.item').forEach(function(item) {
    var option = document.createElement('option');
    option.value = item.id;
    option.textContent = item.textContent;
    select.appendChild(option);
});
}

function updateZIndex() {
var itemId = document.getElementById('itemSelect').value;
var zIndex = document.getElementById('zIndex').value;
document.getElementById(itemId).style.zIndex = zIndex;
}

// Initialize existing items
document.querySelectorAll('.item').forEach(initializeInteract);
updateItemSelect();
























function addNewChart() {
chartCount++;
let chartId = 'chart' + chartCount;
let chartContainer = document.createElement('div');
chartContainer.className = 'chart-container';
chartContainer.setAttribute('data-chart-id', chartId);
chartContainer.style.width = '300px';
chartContainer.style.height = '200px';

let canvas = document.createElement('canvas');
canvas.id = chartId;
chartContainer.appendChild(canvas);

document.getElementById('container').appendChild(chartContainer);
initializeInteract(chartContainer);

// Fetch data and create chart
fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        let ctx = document.getElementById(chartId).getContext('2d');
        charts[chartId] = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
}









function loadDashboardList() {
fetch('/api/list_dashboards')
    .then(response => response.json())
    .then(dashboards => {
        let select = document.getElementById('dashboardSelect');
        select.innerHTML = '<option value="">Select a dashboard</option>';
        dashboards.forEach(dashboard => {
            let option = document.createElement('option');
            option.value = dashboard.id;
            option.textContent = dashboard.id;
            select.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to load dashboard list');
    });
}

// Call this function when the page loads
document.addEventListener('DOMContentLoaded', loadDashboardList);




















let chartCount = 0;
let charts = {};







function saveDashboard() {
let dashboardName = document.getElementById('dashboardName').value;
if (!dashboardName) {
    alert('Please enter a dashboard name');
    return;
}

let dashboard = {
    id: dashboardName,
    name: dashboardName,
    layout: [],
    charts: []
};

document.querySelectorAll('.chart-container').forEach(container => {
    let chartId = container.getAttribute('data-chart-id');
    let chart = charts[chartId];
    
    dashboard.layout.push({
        id: chartId,
        x: container.getAttribute('data-x') || 0,
        y: container.getAttribute('data-y') || 0,
        width: container.style.width,
        height: container.style.height
    });

    dashboard.charts.push({
        id: chartId,
        type: chart.config.type,
        options: chart.options,
        data: {
            labels: chart.data.labels,
            datasets: chart.data.datasets.map(dataset => ({
                label: dataset.label,
                dataSource: dataset.dataSource || '/api/data'  // Example: store data source instead of actual data
            }))
        }
    });
});

fetch('/api/save_dashboard', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dashboard),
})
.then(response => response.json())
.then(data => {
    alert('Dashboard saved with name: ' + dashboard.name);
    document.getElementById('dashboardName').value = '';
    loadDashboardList();  // Refresh the list of dashboards
})
.catch(error => {
    console.error('Error:', error);
    alert('Failed to save dashboard');
});
}

function loadDashboard(dashboardId) {
fetch('/api/load_dashboard/' + encodeURIComponent(dashboardId))
    .then(response => {
        if (!response.ok) throw new Error('Dashboard not found');
        return response.json();
    })
    .then(dashboard => {
        document.getElementById('container').innerHTML = '';
        let charts = {};
        let chartCount = 0;

        // Ensure dashboard.layout and dashboard.charts exist and are arrays
        if (Array.isArray(dashboard.layout)) {
            dashboard.layout.forEach(item => {
                let chartContainer = document.createElement('div');
                chartContainer.className = 'chart-container';
                chartContainer.setAttribute('data-chart-id', item.id);
                chartContainer.style.width = item.width;
                chartContainer.style.height = item.height;
                chartContainer.style.transform = `translate(${item.x}px, ${item.y}px)`;
                chartContainer.setAttribute('data-x', item.x);
                chartContainer.setAttribute('data-y', item.y);
                
                let canvas = document.createElement('canvas');
                canvas.id = item.id;
                chartContainer.appendChild(canvas);
                
                document.getElementById('container').appendChild(chartContainer);
                initializeInteract(chartContainer);  // Make sure this function is defined
            });
        }

        if (Array.isArray(dashboard.charts)) {
            dashboard.charts.forEach(chartConfig => {
                fetch(chartConfig.data.datasets[0].dataSource)
                    .then(response => response.json())
                    .then(data => {
                        let ctx = document.getElementById(chartConfig.id).getContext('2d');
                        charts[chartConfig.id] = new Chart(ctx, {
                            type: chartConfig.type,
                            data: {
                                labels: chartConfig.data.labels,
                                datasets: [{
                                    label: chartConfig.data.datasets[0].label,
                                    data: data.datasets[0].data,
                                    // Add other dataset properties as needed
                                }]
                            },
                            options: chartConfig.options
                        });
                    });
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to load dashboard: ' + error.message);
    });
}




function loadSelectedDashboard() {
let dashboardId = document.getElementById('dashboardSelect').value;
if (!dashboardId) {
    alert('Please select a dashboard to load');
    return;
}
loadDashboard(dashboardId);
}

















document.querySelectorAll('.item').forEach(item => {
    item.addEventListener('click', function() {
        // Toggle the 'clicked' class on the clicked item
        this.classList.toggle('clicked');
    });
});


