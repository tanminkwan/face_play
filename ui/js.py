js_to_network_graph_tab=\
"""
function() {
    // Find the tab button whose text is "Network Graph" and click it.
    const tabs = document.querySelectorAll('button[role="tab"]');
    for (let t of tabs) {
        if (t.innerText.trim() === "Network Graph") {
            t.click();
            break;
        }
    }
    return [];
}
"""

js_send_faceid_to_selectedid=\
"""
function(...args) {
    window.rowClick = function(faceId, fileName) {
        console.log("Here!! Here!!", faceId, fileName);

        // (1) selected_id 영역
        const containerSelectedId = document.getElementById("selected_id");
        if (containerSelectedId) {
            const textboxSelectedId = containerSelectedId.querySelector("textarea");
            if (textboxSelectedId) {
                textboxSelectedId.value = faceId;
                const event = new Event("input", { bubbles: true });
                textboxSelectedId.dispatchEvent(event);
            } else {
                console.log("No <textarea> inside #selected_id");
            }
        } else {
            console.log("No element with id='selected_id'");
        }

        // (2) original_file_name 영역
        const containerFileName = document.getElementById("original_file_name");
        if (containerFileName) {
            const textboxFileName = containerFileName.querySelector("textarea");
            if (textboxFileName) {
                textboxFileName.value = fileName;
                const event = new Event("input", { bubbles: true });
                textboxFileName.dispatchEvent(event);
            } else {
                console.log("No <textarea> inside #original_file_name");
            }
        } else {
            console.log("No element with id='original_file_name'");
        }
    }
}
"""