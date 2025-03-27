var database;

function send_data(msg) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(['database_host'], function(result) {
            if (result.database_host) {
                console.log('database_host currently is ' + result.database_host);
                database = "http://"+result.database_host+":7866/endpoint";
            } else {
                database = "http://127.0.0.1:7866/endpoint";
            }
            fetch(database, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(msg),
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                resolve(data);
            })
            .catch((error) => {
                console.error('Error:', error);
                reject(error);
            });
        });
    });
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.flag == "open_tab_and_cache_from_content") {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0] && msg.data) {
                const url = tabs[0].url;
                console.log(url);
                send_data({ 'content': msg.data, 'query': '', 'url': url, 'task': 'cache', 'type': msg.type })
                    .then(data => {
                        sendResponse(data);
                    })
                    .catch(error => {
                        console.error('Error caching page:', error);
                        sendResponse({ error: 'Failed to cache page' });
                    });
            }
        });
        return true; // Will respond asynchronously
    }
    if (msg.flag == "open_popup_and_send_url_from_popup") {
        if (msg.data) {
            send_data({ 'url': msg.data, 'task': 'pop_url' })
                .then(data => {
                    sendResponse(data);
                })
                .catch(error => {
                    console.error('Error updating popup URL:', error);
                    sendResponse({ error: 'Failed to update popup URL' });
                });
        }
        return true; // Will respond asynchronously
    }
    if (msg.flag == "check_page_exists") {
        send_data({ 'url': msg.url, 'task': 'check_page' })
            .then(data => {
                sendResponse(data);
            })
            .catch(error => {
                console.error('Error checking page:', error);
                sendResponse({ exists: false });
            });
        return true; // Will respond asynchronously
    }
});
