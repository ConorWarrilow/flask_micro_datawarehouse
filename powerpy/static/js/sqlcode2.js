

// Initialize CodeMirror
document.addEventListener('DOMContentLoaded', function() {
    const databaseSelector = document.getElementById('database-dropdown-selector');
    const schemaSelector = document.getElementById('schema-dropdown-selector');
    const runQueryButton = document.getElementById('run-query');
    const sqlOutput = document.getElementById('sql-output');
    const lineNumbersContainer = document.getElementById('code-line-numbers');
    const codeMirrorLineNumbers = document.getElementById('')
    const username = document.body.dataset.username; // Assume you set the username as a data attribute on the body
    let databaseMap = new Map();
    let schemaMap = new Map();
    const ROW_HEIGHT = 30; // Adjust based on your CSS
    const VISIBLE_ROWS = 30; // Number of rows to render at once
    const timer=queryTimer();

    // Initialize CodeMirror
    var editor = CodeMirror.fromTextArea(document.getElementById("sql-editor"), {
        mode: "text/x-sql",
        theme: "solarized dark",
        lineNumbers: false, // Disable default line numbers
        viewportMargin: Infinity,
        lineWrapping: true,
        extraKeys: {
            "Ctrl-Space": "autocomplete",
            "Ctrl-Enter": function(cm) {
                runQuery(); // Call the query execution function
            }
        },
        hintOptions: {
            tables: {
                users: ["id", "name", "email", "created_at"],
                orders: ["order_id", "user_id", "product_id", "quantity", "price"],
                products: ["product_id", "product_name", "price", "stock"],
                categories: ["category_id", "category_name"]
            }
        },

    });



    // Function to update line numbers
    function updateLineNumbers() {
        const totalLines = editor.lineCount();
        let lineNumbersHTML = '';
        for (let i = 1; i <= totalLines; i++) {
            lineNumbersHTML += `<div class="line-number" data-line="${i}">${i}</div>`;
        }
        lineNumbersContainer.innerHTML = lineNumbersHTML;
    }

    // Update line numbers initially and on change
    updateLineNumbers();
    editor.on('change', updateLineNumbers);

    // Synchronize scrolling
    editor.on('scroll', function() {
        const scrollInfo = editor.getScrollInfo();
        lineNumbersContainer.scrollTop = scrollInfo.top;
    });

    // Function to get the query at the current cursor position
    function getQueryAtCursor() {
        const content = editor.getValue();
        const cursor = editor.getCursor();
        const lines = content.split('\n');
        
        let currentLine = cursor.line;
        let queryStart = currentLine;
        let queryEnd = currentLine;

        // Find the start of the query (move up until we find a line with a semicolon or reach the top)
        while (queryStart > 0 && !lines[queryStart - 1].trim().endsWith(';')) {
            queryStart--;
        }

        // Find the end of the query (move down until we find a line with a semicolon or reach the bottom)
        while (queryEnd < lines.length - 1 && !lines[queryEnd].trim().endsWith(';')) {
            queryEnd++;
        }

        // Extract the query
        const query = lines.slice(queryStart, queryEnd + 1).join('\n').trim();

        return {
            query: query.endsWith(';') ? query : query + ';',
            startLine: queryStart + 1,
            endLine: queryEnd + 1
        };
    }

    // Run query
    function runQuery() {
        const { query, startLine, endLine } = getQueryAtCursor();
        if (!query) {
            console.log('No valid query at cursor position');
            sqlOutput.innerHTML = '<p>No valid query at cursor position</p>';
            return;
        }
        const svgIcon = `
        <i class="fas fa-exclamation-triangle" style="font-size:30px; color:#b58900; margin-bottom:15px;"></i>
        `;
        // Highlight the executed lines
        highlightExecutedLines(startLine, endLine);

        timer.startTimer();


        const selectedDatabaseName = databaseMap.get(databaseSelector.value);
        const selectedSchemaName = schemaMap.get(schemaSelector.value);

        console.log('Sending query:', query);
        console.log('Selected database:', selectedDatabaseName);
        console.log('Selected schema:', selectedSchemaName);

        fetch(`/editor?selected_database=${encodeURIComponent(selectedDatabaseName)}&selected_schema=${encodeURIComponent(selectedSchemaName)}&query=${encodeURIComponent(query)}`)
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                displayResults(data);  // Call your function to display results
            })
            .catch(error => {
                console.error('Error:', error);
                sqlOutput.innerHTML = `<p>Error: ${error.message}</p>`;
            });
    }

    // Function to highlight executed lines
    function highlightExecutedLines(startLine, endLine) {
        // Remove previous highlights
        const lineNumbers = lineNumbersContainer.querySelectorAll('.line-number');
        lineNumbers.forEach(lineNumber => lineNumber.classList.remove('executed'));

        // Add highlight to executed lines
        for (let i = startLine; i <= endLine; i++) {
            const lineNumber = lineNumbersContainer.querySelector(`[data-line="${i}"]`);
            if (lineNumber) {
                lineNumber.classList.add('executed');
            }
        }
    }

    // Attach the runQuery function to the run button
    runQueryButton.addEventListener('click', runQuery);





    function displayResults(data) {
        if (data.error) {
            const svgIcon = `
                <i class="fas fa-exclamation-triangle" style="font-size:30px; color:#b58900; margin-bottom:15px;"></i>
            `;
    
            sqlOutput.innerHTML = `<div class="query-error-message">${svgIcon}<br> ${data.error}</div>`;
            return;
        }
    
    
        allData = data.data;
        const totalHeight = allData.length * ROW_HEIGHT;
    
        let tableHtml = `
            <div class="table-container" style="height: ${VISIBLE_ROWS * ROW_HEIGHT}px; overflow-y: auto;">
                <table class="sql-result-table">
                    <thead>
                        <tr>
                            ${data.columns.map(column => `<th class="sql-table-header">${column}<div class="resizer"></div></th>`).join('')}
                        </tr>
                    </thead>
                    <tbody style="position: relative; height: ${totalHeight}px;">
                    </tbody>
                </table>
            </div>
        `;
    
        sqlOutput.innerHTML = tableHtml;
        
        timer.stopAndReset();

        const tableContainer = document.querySelector('.table-container');
        tableContainer.addEventListener('scroll', handleScroll);
    
        generateRows(0);
        setupColumnResizing();
        updateTableWidth();
    }
    
    function generateRows(startIndex) {
        const endIndex = Math.min(startIndex + VISIBLE_ROWS, allData.length);
        visibleData = allData.slice(startIndex, endIndex);
    
        const tbody = document.querySelector('.sql-result-table tbody');
        tbody.innerHTML = '';
    
        visibleData.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.className = 'sql-table-row';
            tr.style.position = 'absolute';
            tr.style.top = `${(startIndex + index) * ROW_HEIGHT}px`;
            tr.style.left = '0';
            tr.style.right = '0';
    
            row.forEach((cell, cellIndex) => {
                const td = document.createElement('td');
                td.className = 'sql-table-cell';
                td.textContent = cell;
                tr.appendChild(td);
            });
    
            tbody.appendChild(tr);
        });
    
        updateColumnWidths();
    }
    
    function updateColumnWidths() {
        const headers = document.querySelectorAll('.sql-table-header');
        headers.forEach((header, index) => {
            const width = header.offsetWidth;
            const cells = document.querySelectorAll(`.sql-table-row td:nth-child(${index + 1})`);
            cells.forEach(cell => cell.style.width = `${width}px`);
        });
    }
    
    function handleScroll(e) {
        const scrollTop = e.target.scrollTop;
        const startIndex = Math.floor(scrollTop / ROW_HEIGHT);
    
        generateRows(startIndex);
    }
    
    function setupColumnResizing() {
        const table = document.querySelector('.sql-result-table');
        const cols = table.querySelectorAll('th');
        let draggedCol = null;
    
        cols.forEach((col, index) => {
            const resizer = col.querySelector('.resizer');
            resizer.addEventListener('mousedown', (e) => {
                e.preventDefault();
                draggedCol = {col, index};
                const startX = e.pageX;
                const startWidth = col.offsetWidth;
    
                const mouseMoveHandler = (e) => {
                    if (draggedCol) {
                        const diff = e.pageX - startX;
                        const newWidth = Math.max(startWidth + diff, 100); // Minimum width of 20px
                        draggedCol.col.style.width = `${newWidth}px`;
                        
                        // Update only the cells in this column
                        const cells = table.querySelectorAll(`td:nth-child(${draggedCol.index + 1})`);
                        cells.forEach(cell => {
                            cell.style.width = `${newWidth}px`;
                        });
    
                        // Adjust the position of subsequent columns
                        let accumulatedOffset = 0;
                        for (let i = 0; i <= draggedCol.index; i++) {
                            const currentCol = cols[i];
                            accumulatedOffset += currentCol.offsetWidth;
                        }
    
                        // Adjust the position of the cells in the current and subsequent columns
                        for (let i = draggedCol.index + 1; i < cols.length; i++) {
                            const nextCol = cols[i];
                            nextCol.style.left = `${accumulatedOffset}px`;
                            const nextCells = table.querySelectorAll(`td:nth-child(${i + 1})`);
                            nextCells.forEach(cell => {
                                cell.style.left = `${accumulatedOffset}px`;
                            });
                            accumulatedOffset += nextCol.offsetWidth;
                        }
                    }
                };
    
                const mouseUpHandler = () => {
                    draggedCol = null;
                    document.removeEventListener('mousemove', mouseMoveHandler);
                    document.removeEventListener('mouseup', mouseUpHandler);
                    updateColumnWidths(); // Ensure all widths are properly set after resizing
                };
    
                document.addEventListener('mousemove', mouseMoveHandler);
                document.addEventListener('mouseup', mouseUpHandler);
            });
        });
    }
    
    function updateTableWidth() {
        const headers = document.querySelectorAll('.sql-table-header');
        const totalWidth = Array.from(headers).reduce((sum, header) => sum + header.offsetWidth, 0);
        document.querySelector('.sql-result-table').style.width = `${totalWidth}px`;
    }

    // Bind the button click event to the runQuery function
    runQueryButton.addEventListener('click', runQuery);






    

    // Load databases
    fetch(`/databases`)
        .then(response => response.json())
        .then(data => {
            data.forEach(db => {
                const [id, name] = db;
                databaseMap.set(id, name);
                const option = document.createElement('option');
                option.value = id;
                option.textContent = name;
                databaseSelector.appendChild(option);
            });
            // Load schemas for the first database
            if (databaseSelector.value) {
                loadSchemas(databaseSelector.value);
            }
        });

    // Load schemas when database selection changes
    databaseSelector.addEventListener('change', function() {
        loadSchemas(this.value);
    });

    function loadSchemas(databaseId) {
        schemaSelector.innerHTML = '';
        schemaMap.clear();
        fetch(`/${username}/databases/${databaseId}/schemas`)
            .then(response => response.json())
            .then(data => {
                data.forEach(schema => {
                    const [id, name] = schema;
                    schemaMap.set(id, name);
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = name;
                    schemaSelector.appendChild(option);
                });
            });
    }






    function saveWorksheet() {
        console.log('saveWorksheet function called');
        const content = editor.getValue();
        const code = window.location.pathname.split('/').pop();
        const username = document.body.getAttribute('data-username');
    
        console.log(`Saving worksheet: username=${username}, code=${code}, content length=${content.length}`);
    
        fetch(`/${username}/query/${code}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Worksheet saved:', data);
        })
        .catch((error) => {
            console.error('Error saving worksheet:', error);
        });
    }
    
    function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
    
    // Set up auto-save
    let saveTimeout;
    const saveDelay = 60000; // 1 minute
    
    // Use CodeMirror's 'change' event instead of 'input' event
    editor.on('change', function() {
        console.log('Change detected in CodeMirror editor');
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            console.log('Timeout triggered, calling saveWorksheet');
            saveWorksheet();
        }, saveDelay);
    });
    
    window.addEventListener('beforeunload', function(e) {
        console.log('Page unloading, saving worksheet');
        saveWorksheet();
    });
    
    // Initial save when the page loads
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOMContentLoaded, calling initial saveWorksheet');
        saveWorksheet();
    });
    












});





function queryTimer(){
    const sqlOutput = document.getElementById('sql-output');
    let isRunning = false;
    let startTime = 0
    let elapsedTime = 0

    function startTimer(){
        if(!isRunning){
            startTime = Date.now() - elapsedTime;
            timer = setInterval(update, 10)
            isRunning=true;
        }

    }

    function update(){
        const currentTime = Date.now();
        elapsedTime = currentTime-startTime;

        let minutes = Math.floor(elapsedTime / (60000) % 60);
        let seconds = Math.floor(elapsedTime / 1000 % 60);
        let milliseconds = Math.floor(elapsedTime % 1000 / 10);

        minutes = String(minutes).padStart(2, "0")
        seconds = String(seconds).padStart(2, "0")
        milliseconds = String(milliseconds).padStart(2, "0")


        sqlOutput.innerHTML = `<div class="query-error-message">${minutes}:${milliseconds}</div>`;

    }

    function stopAndReset() {
        clearInterval(timer)
        elapsedTime = 0;
        isRunning = false
    }

    return {startTimer, stopAndReset}
}