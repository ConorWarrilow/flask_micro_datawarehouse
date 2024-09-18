document.addEventListener('DOMContentLoaded', function() {
    const databaseButtons = document.querySelectorAll('.database-dropdown-button');

    databaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const databaseId = this.dataset.databaseId;
            const username = this.dataset.username; // Get the username from the data attribute (used for the api )
            const schemaContainer = this.nextElementSibling; // selects the schema-container div
            const icon = this.querySelector('i'); // Select the Font Awesome arrow icon

            console.log(icon)
            if (schemaContainer.style.display === 'none') {
                // Change icon to fa-angle-down
                icon.classList.remove('fa-angle-right');
                icon.classList.add('fa-angle-down');
                
                // Load schemas
                fetch(`/${username}/databases/${databaseId}/schemas`)
                    .then(response => response.json())
                    .then(schemas => {
                        schemaContainer.innerHTML = ''; // making sure its empty
                        schemas.forEach(schema => {
                            const schemaItem = document.createElement('div'); // creates a div for each schema
                            schemaItem.className = 'schema-item'; // applying the schema-item class to each schema
                            // the api sends the schema id (index 0) and the schema name (index 1)
                            schemaItem.innerHTML = `
                                <div class="tree-item">
                                    <div class="tree-line"></div>
                                    <button class="schema-dropdown-button" data-schema-id="${schema[0]}">
                                        <div class="button-left-content">
                                            <i class="fas fa-angle-right arrow-icon"></i> 
                                            <i class="custom-icon fas fa-project-diagram"></i>
                                            <span class="button-text">${schema[1]}</span>
                                        </div>
                                        <div class="button-ellipsis">
                                            <i class="fa-solid fa-ellipsis"></i>
                                        </div>
                                    </button>
                                </div>
                            `; 

                            
                            const datafileContainer = document.createElement('div');
                            datafileContainer.className = 'datafile-container';
                            datafileContainer.style.display = 'none';
                            
                            // Now we Handle schema dropdown button click for fetching the datafiles
                            schemaItem.querySelector('.schema-dropdown-button').addEventListener('click', function(e) {
                                //e.stopPropagation(); // not needed, the schema button isn't contained within (not a child element) the database button, the schema button is the next element sibling
                                const schemaId = this.dataset.schemaId; // dataset is a built in property in Javascript. use data-schema-id =... in the html
                                const schemaIcon = this.querySelector('i'); // Select the Font Awesome icon for schema
                                
                                if (datafileContainer.style.display === 'none') {
                                    // Change icon to fa-angle-down
                                    schemaIcon.classList.remove('fa-angle-right');
                                    schemaIcon.classList.add('fa-angle-down');
                                    
                                    // Load datafiles
                                    fetch(`/${username}/schemas/${schemaId}/datafiles`)
                                        .then(response => response.json())
                                        .then(datafiles => {
                                            datafileContainer.innerHTML = '';
                                            datafiles.forEach(datafile => {
                                                const datafileItem = document.createElement('div');
                                                datafileItem.className = 'datafile-item';
                                                datafileItem.innerHTML = `
                                                    <div class="tree-item">
                                                        <div class="tree-line"></div>
                                                        <div class="tree-line-two"></div>
                                                        <button class="datafile-button">
                                                            <div class="button-left-content">
                                                                <i class="custom-icon fa fa-table" aria-hidden="true"></i>
                                                                <span class="button-text">${datafile[1]}</span>
                                                            </div>
                                                            <div class="button-ellipsis">
                                                                <i class="fa-solid fa-ellipsis"></i>
                                                            </div>
                                                        </button>
                                                    </div>
                                                `;
                                                datafileContainer.appendChild(datafileItem);
                                            });
                                            datafileContainer.style.display = 'block';
                                        });
                                } else {
                                    // Change icon back to fa-angle-right
                                    schemaIcon.classList.remove('fa-angle-down');
                                    schemaIcon.classList.add('fa-angle-right');
                                    datafileContainer.style.display = 'none';
                                }
                            });
                            
                            schemaContainer.appendChild(schemaItem);
                            schemaContainer.appendChild(datafileContainer);
                        });
                        schemaContainer.style.display = 'block';
                    });
            } else {
                // Change icon back to fa-angle-right
                icon.classList.remove('fa-angle-down');
                icon.classList.add('fa-angle-right');
                schemaContainer.style.display = 'none';
            }
        });
    });
});




function filterLeftSectionContents() {
    const leftSectionContents = document.getElementsByClassName("left-section-contents")
    console.log(leftSectionContents)
}

filterLeftSectionContents()