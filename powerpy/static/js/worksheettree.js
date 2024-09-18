

/**
 * This script sets up interactive folder dropdown functionality on the page.
 * It listens for the 'DOMContentLoaded' event to ensure the DOM is fully loaded before executing the script.
 * 
 * Functionality Overview:
 * - The script targets all elements with the class 'folder-dropdown-button', which are expected to be folder buttons.
 * - For each button, a click event listener is attached that toggles the visibility of associated folder and worksheet containers.
 * 
 * Detailed Behavior:
 * 1. When the page content has fully loaded, the script queries all elements with the class 'folder-dropdown-button'.
 * 
 * 2. Each folder button is then assigned a click event listener. When a button is clicked:
 *    - The script retrieves the folder ID and username from the button's data attributes.
 *    - It then identifies the adjacent elements for child folder and worksheet containers.
 *    - It also selects the Font Awesome icon within the button to change its appearance based on the toggle state.
 * 
 * 3. If both the child folder and worksheet containers are currently hidden (i.e., their display style is set to 'none'):
 *    - The script updates the icon to indicate that the folder is expanded by changing it from 'fa-angle-right' to 'fa-angle-down'.
 *    - It then makes a fetch request to retrieve the contents of the folder from the server. The request URL is constructed using the folder ID and username.
 *    - Upon receiving the response, which is expected to be a JSON array containing child folders and worksheets, it:
 *      - Clears the existing content in both the child folder and worksheet containers.
 *      - Iterates over the child folders and worksheets, creating and appending HTML elements for each.
 *      - Sets the display style of both containers to 'block' to make them visible.
 * 
 * 4. If either container is currently visible:
 *    - The script reverts the icon back to its original state ('fa-angle-right') to indicate that the folder is collapsed.
 *    - It hides both the child folder and worksheet containers by setting their display style to 'none'.
 * 
 * This approach ensures that the user can toggle between expanding and collapsing folder contents, with a visual indication provided by the Font Awesome icon.
 */
document.addEventListener('DOMContentLoaded', function() {
    const folderButtons = document.querySelectorAll('.folder-dropdown-button');
    const worksheetButtons = document.querySelectorAll('.worksheet-button');

    worksheetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const worksheetCode = this.dataset.worksheetCode;
            const username = this.dataset.worksheetUsername;
            window.location.href = `/${username}/query/${worksheetCode}`
        });
    });




    folderButtons.forEach(button => {
        button.addEventListener('click', function() {
            const folderId = this.dataset.folderId;
            const username = this.dataset.username;
            const childFolderContainer = this.nextElementSibling;
            console.log(`child folder container: ${childFolderContainer}`)
            const childWorksheetContainer = childFolderContainer.nextElementSibling;
            const icon = this.querySelector('i.fas'); // Select the Font Awesome icon

            if (childFolderContainer.style.display === 'none' && childWorksheetContainer.style.display === 'none') {
                // Change icon to fa-angle-down
                icon.classList.remove('fa-angle-right');
                icon.classList.add('fa-angle-down');
                
                // Load folder contents
                fetch(`/${username}/worksheets/${folderId}/worksheets`)
                    .then(response => response.json())
                    .then(data => {
                        const [folders, worksheets] = data;
                        
                        // Clear existing content
                        childFolderContainer.innerHTML = '';
                        childWorksheetContainer.innerHTML = '';

                        // Add child folders
                        folders.forEach(folder => {
                            const folderItem = createFolderItem(folder, username);
                            childFolderContainer.appendChild(folderItem);
                        });

                        // Add worksheets
                        worksheets.forEach(worksheet => {
                            const worksheetItem = createWorksheetItem(worksheet, username, false);
                            childWorksheetContainer.appendChild(worksheetItem);
                        });

                        childFolderContainer.style.display = 'block';
                        childWorksheetContainer.style.display = 'block';
                    });
            } else {
                // Change icon back to fa-angle-right
                icon.classList.remove('fa-angle-down');
                icon.classList.add('fa-angle-right');
                childFolderContainer.style.display = 'none';
                childWorksheetContainer.style.display = 'none';
            }
        });
    });

});

// function used to create child folders. this function is called multiple times in the above event listener (assuming a folder has multiple child folders)

function createFolderItem(folder, username) {
    const [folderId, folderName] = folder;
    const folderItem = document.createElement('div');
    folderItem.className = 'worksheet-item';
    folderItem.innerHTML = `
        <div class="tree-item">
            <div class="tree-line"></div>
            <button class="folder-dropdown-button" data-folder-id="${folderId}" data-username="${username}">
                <div class="button-left-content">
                    <i class=" fas fa-angle-right arrow-icon"></i>
                    <i class="custom-icon far fa-folder"></i>
                    <span class="button-text">${folderName}</span>
                </div>
                <div class="button-ellipsis">
                    <i class="fa-solid fa-ellipsis"></i>
                </div>
            </button>
        </div>
        <div class="child-folder-container" style="display: none;"></div>
        <div class="child-worksheet-container" style="display: none;"></div>
    `;

    // Add click event listener to the new folder button
    const newFolderButton = folderItem.querySelector('.folder-dropdown-button');
    newFolderButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const folderId = this.dataset.folderId;
        const username = this.dataset.username;
        const childFolderContainer = this.closest('.worksheet-item').querySelector('.child-folder-container');
        const childWorksheetContainer = this.closest('.worksheet-item').querySelector('.child-worksheet-container');
        const icon = this.querySelector('i');

        if (childFolderContainer.style.display === 'none' && childWorksheetContainer.style.display === 'none') {
            // Change icon to fa-angle-down
            icon.classList.remove('fa-angle-right');
            icon.classList.add('fa-angle-down');
            
            // Load folder contents
            fetch(`/${username}/worksheets/${folderId}/worksheets`)
                .then(response => response.json())
                .then(data => {
                    const [folders, worksheets] = data;
                    
                    // Clear existing content
                    childFolderContainer.innerHTML = '';
                    childWorksheetContainer.innerHTML = '';

                    // Add child folders
                    folders.forEach(folder => {
                        const folderItem = createFolderItem(folder, username);
                        childFolderContainer.appendChild(folderItem);
                    });

                    // Add worksheets
                    worksheets.forEach(worksheet => {
                        const worksheetItem = createWorksheetItem(worksheet, username, true);
                        childWorksheetContainer.appendChild(worksheetItem);
                    });

                    childFolderContainer.style.display = 'block';
                    childWorksheetContainer.style.display = 'block';
                });
        } else {
            // Change icon back to fa-angle-right
            icon.classList.remove('fa-angle-down');
            icon.classList.add('fa-angle-right');
            childFolderContainer.style.display = 'none';
            childWorksheetContainer.style.display = 'none';
        }
    });

    return folderItem;
}

/* in the above, we basically fill the child folder with the root folder's format */




function createWorksheetItem(worksheet, username, fromChildFolder) {
    const [worksheetCode, worksheetName] = worksheet;
    const worksheetItem = document.createElement('div');
    worksheetItem.className = 'worksheet-item';

    if(fromChildFolder){
        worksheetItem.innerHTML = `
        <div class="tree-item">
            <div class="tree-line"></div>
            <div class="tree-line-two"></div>
            <button class="worksheet-button" data-worksheet-username="${username}" data-worksheet-code="${worksheetCode}">
                <div class="button-left-content">
                    <i class="custom-icon far fa-file-alt"></i>
                    <span class="button-text">${worksheetName}</span>
                </div>
                <div class="button-ellipsis">
                    <i class="fa-solid fa-ellipsis"></i>
                </div>
            </button>
        </div>
    `;
    } else {
        worksheetItem.innerHTML = `
        <div class="tree-item">
            <div class="tree-line"></div>
            <button class="worksheet-button" data-worksheet-username="${username}" data-worksheet-code="${worksheetCode}">
                <div class="button-left-content">
                    <i class="custom-icon far fa-file-alt"></i>
                    <span class="button-text">${worksheetName}</span>
                </div>
                <div class="button-ellipsis">
                    <i class="fa-solid fa-ellipsis"></i>
                </div>
            </button>
        </div>
    `;
    }

    const newWorksheetButton = worksheetItem.querySelector('.worksheet-button')
    newWorksheetButton.addEventListener('click', () => {
        window.location.href = `/${username}/query/${worksheetCode}`
    })

    return worksheetItem;
}



