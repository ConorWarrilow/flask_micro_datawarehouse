

// sliding line for menu buttons
document.addEventListener('DOMContentLoaded', function() {
    const menuButtons = document.querySelectorAll('.menu-button');
    const slidingUnderline = document.querySelector('.sliding-underline');

    function updateUnderline(button) {
        const buttonRect = button.getBoundingClientRect();
        const menuRect = button.parentElement.getBoundingClientRect();

        slidingUnderline.style.width = `${buttonRect.width}px`;
        slidingUnderline.style.left = `${buttonRect.left - menuRect.left}px`;
    }

    function setActiveButton(clickedButton) {
        menuButtons.forEach(button => button.classList.remove('active'));
        clickedButton.classList.add('active');
        updateUnderline(clickedButton);
    }

    menuButtons.forEach(button => {
        button.addEventListener('click', function() {
            setActiveButton(this);
        });
    });

    // Initialize the underline position
    const activeButton = document.querySelector('.menu-button.active') || menuButtons[0];
    updateUnderline(activeButton);

    // Update underline position on window resize
    window.addEventListener('resize', () => {
        const activeButton = document.querySelector('.menu-button.active') || menuButtons[0];
        updateUnderline(activeButton);
    });
});





// switch between displaying databases and worksheets
document.addEventListener('DOMContentLoaded', function() {
    const databasesButton = document.getElementById('databases-button');
    const worksheetsButton = document.getElementById('worksheets-button');
    const dashboardsButton = document.getElementById('dashboards-button');

    const databasesContainer = document.getElementById('databases-container');
    const worksheetsContainer = document.getElementById('worksheets-container');
    const dashboardsContainer = document.getElementById('dashboards-container');

    function showDatabases() {
        databasesContainer.style.display = 'block';
        worksheetsContainer.style.display = 'none';
        dashboardsContainer.style.display = 'none';
        databasesButton.classList.add('active');
        worksheetsButton.classList.remove('active');
        dashboardsButton.classList.remove('active');
    }

    function showWorksheets() {
        databasesContainer.style.display = 'none';
        worksheetsContainer.style.display = 'block';
        dashboardsContainer.style.display = 'none';
        worksheetsButton.classList.add('active');
        databasesButton.classList.remove('active');
        dashboardsButton.classList.remove('active');
    }

    function showDashboards() {
        databasesContainer.style.display = 'none';
        worksheetsContainer.style.display = 'none';
        dashboardsContainer.style.display = 'block';
        dashboardsButton.classList.add('active');
        worksheetsButton.classList.remove('active');
        databasesButton.classList.remove('active');
    }




    databasesButton.addEventListener('click', showDatabases);
    worksheetsButton.addEventListener('click', showWorksheets);
    dashboardsButton.addEventListener('click', showDashboards);

    // Show worksheets by default
    showWorksheets();
});




document.addEventListener('DOMContentLoaded', function() {
    const username = document.body.dataset.username;
    const dashboardButtons = document.querySelectorAll('.dashboard-button')
    dashboardButtons.forEach(button => {

        button.addEventListener('click', function(){

            const dashboardCode = this.dataset.dashboardCode;
             window.location.href = `/${username}/dashboard/${dashboardCode}`
        })
    })
})




const username = document.body.dataset.username;




// ------------ menu buttons ----------------

document.addEventListener('DOMContentLoaded', function() {
    const menuDatabaseButton = document.getElementById('main-menu-home-button')

    menuDatabaseButton.addEventListener('click', function(){
        window.location.href = `/${username}/home`
    })
})

document.addEventListener('DOMContentLoaded', function() {
    const menuDatabaseButton = document.getElementById('main-menu-databases-button')

    menuDatabaseButton.addEventListener('click', function(){
        window.location.href = `/${username}/databases`
    })
})

document.addEventListener('DOMContentLoaded', function() {
    const menuDatabaseButton = document.getElementById('main-menu-dashboards-button')

    menuDatabaseButton.addEventListener('click', function(){
        window.location.href = `/${username}/dashboards`
    })
})

document.addEventListener('DOMContentLoaded', function() {
    const menuDatabaseButton = document.getElementById('main-menu-worksheets-button')

    menuDatabaseButton.addEventListener('click', function(){
        window.location.href = `/${username}/worksheets`
    })
})

document.addEventListener('DOMContentLoaded', function() {
    const menuDatabaseButton = document.getElementById('main-menu-account-button')

    menuDatabaseButton.addEventListener('click', function(){
        window.location.href = `/${username}/account`
    })
})