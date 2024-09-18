
function initHorizontalResize(resizer) {
    const leftSection = resizer.previousElementSibling;
    const rightSection = resizer.nextElementSibling;
    const leftSectionMenu = document.querySelector(".left-section-menu");
    const leftSectionContents = document.querySelector(".left-section-contents")
    let startX, startWidth;

    function startResize(e) {
        startX = e.clientX;
        startWidth = parseInt(getComputedStyle(leftSection).width, 10);
        document.addEventListener("mousemove", resize);
        document.addEventListener("mouseup", stopResize);
    }

    function resize(e) {
        const diff = e.clientX - startX;
        const newWidthLeft = startWidth + diff;

        // Handle collapsing the left section smoothly
        if (newWidthLeft <= 100) {
            leftSection.style.transition = "width 0.2s ease";
            leftSection.style.width = "10px"; // DETERMINES HOW FAR AWAY FROM THE EDGE TO COLLAPSE
            rightSection.style.width = `calc(100% - ${resizer.offsetWidth}px)`;

            // Fade out content
            fadeContent(leftSectionMenu, 0);
            fadeContent(leftSectionContents, 0);

        } else {
            leftSection.style.transition = ""; // Remove transition when resizing
            leftSection.style.width = `${newWidthLeft}px`;
            rightSection.style.width = `calc(100% - ${newWidthLeft}px - ${resizer.offsetWidth}px)`;

            // Fade in content gradually as the width increases
            const fadeFactor = (newWidthLeft - 50) / 100; // Adjust this factor based on your preference
            fadeContent(leftSectionMenu, fadeFactor);
            fadeContent(leftSectionContents, fadeFactor);

        }
    }

    function stopResize() {
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stopResize);

        // Ensure left section width is accurately updated
        if (parseInt(leftSection.style.width, 10) === 0) {
            rightSection.style.width = `calc(100% - ${resizer.offsetWidth}px)`;
        }
    }

    function fadeContent(element, opacity) {
        element.style.transition = "opacity 0.3s ease"; // Smooth fade
        element.style.opacity = opacity;
    }

    resizer.addEventListener("mousedown", startResize);
}










function initVerticalResize(resizer) {
    const topSection = resizer.previousElementSibling;
    const bottomSection = resizer.nextElementSibling;
    let startY, startHeightTop, startHeightBottom;

    function startResize(e) {
        startY = e.clientY;
        startHeightTop = topSection.offsetHeight;
        startHeightBottom = bottomSection.offsetHeight;
        document.addEventListener("mousemove", resize);
        document.addEventListener("mouseup", stopResize);
    }

    function resize(e) {
        const diff = e.clientY - startY;
        const newHeightTop = startHeightTop + diff;
        const newHeightBottom = startHeightBottom - diff;

        // Add a smooth transition when collapsing
        if (newHeightBottom <= 50 && newHeightBottom !== 0) {
            bottomSection.style.transition =
                "height 0.2s ease, borderTop 0.2s ease";
            bottomSection.style.height = "0px";
            bottomSection.style.borderTop = "0px solid #424242";
            topSection.style.height = `${startHeightTop + startHeightBottom}px`;
        } else {
            bottomSection.style.transition = "";
            topSection.style.height = `${newHeightTop}px`;
            bottomSection.style.borderTop = "1px solid #424242";
            bottomSection.style.height = `${newHeightBottom}px`;
        }

        updateTableWidth(); // Update the table width during resizing
    }

    function stopResize() {
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stopResize);

        // Handle case where the bottom section is collapsed
        if (bottomSection.offsetHeight === 0) {
            bottomSection.style.height = "0px"; // Ensure it's fully collapsed

            //topSection.style.height = `calc(100% - ${resizer.offsetHeight}px)`; // Expand top section to full size minus the resizer
        }

        updateTableWidth(); // Update the table width after resizing is complete
    }

    resizer.addEventListener("mousedown", startResize);
}

initHorizontalResize(document.getElementById("horizontalResizer"));
initVerticalResize(document.getElementById("verticalResizer"));
