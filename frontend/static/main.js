function getUrlParams() {
    return new URLSearchParams(window.location.search);
}

window.onload = function() {
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');

    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
    }
    const params = getUrlParams();
    const sortBy = params.get('sort_by');
    const sortOrder = params.get('sort_order');

    if (sortBy) {
        document.getElementById('sort-by-select').value = sortBy;
    }
    if (sortOrder) {
        document.getElementById('sort-order-select').value = sortOrder;
    }
    if (savedBaseUrl) {
        loadPosts();
    }
}

function updateSortUrl() {
    const sortBy = document.getElementById('sort-by-select').value;
    const sortOrder = document.getElementById('sort-order-select').value;
    const params = new URLSearchParams(window.location.search);
    params.set('sort_by', sortBy);
    params.set('sort_order', sortOrder);
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    history.pushState(null, '', newUrl);
    loadPosts();
}
function clearSearchAndLoad() {
    document.getElementById('search-query').value = '';
    document.getElementById('search-by-select').value = 'title'; // Resets to default
    loadPosts();
}

function loadPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl)
    const searchBy = document.getElementById('search-by-select').value;
    const searchQuery = document.getElementById('search-query').value.trim();
    const params = getUrlParams();
    const sortBy = params.get('sort_by') || 'date';
    const sortOrder = params.get('sort_order') || 'desc';

    let apiUrl = baseUrl;
    let queryString = `?sort_by=${sortBy}&sort_order=${sortOrder}`;

    if (searchQuery) {
        apiUrl += '/search';
        const combinedSearchTerm = `${searchBy}:${searchQuery}`;
        queryString = `?query=${encodeURIComponent(combinedSearchTerm)}&sort_by=${sortBy}&sort_order=${sortOrder}`;

    } else {
        apiUrl += '/posts';
    }
    fetch(apiUrl + queryString)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            if (data.length === 0) {
                 postContainer.innerHTML = `<p class="no-posts-message">No posts found matching your criteria. Try a different search term or clear the filter.</p>`;
            }

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';

                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p class="post-meta">By: <strong>${post.author}</strong> on ${post.date}</p>
                    <p>${post.content}</p>
                    <button onclick="deletePost(${post.id})">Delete</button>
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching posts:', error);
            document.getElementById('post-container').innerHTML = `<p class="error-message">Failed to load posts. Check your API URL and server status: ${error.message}</p>`;
        });
}

function addPost() {
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;

    if (!postTitle || !postContent || !postAuthor) {
        alert('Please fill in the Title, Content, and Author fields.');
        return;
    }

    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const postDate = `${yyyy}-${mm}-${dd}`;

    const postData = {
        title: postTitle,
        content: postContent,
        author: postAuthor,
        date: postDate
    };

    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || `HTTP error! Status: ${response.status}`); });
        }
        return response.json();
    })
    .then(post => {
        console.log('Post added:', post);
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        document.getElementById('post-author').value = '';
        loadPosts();
    })
    .catch(error => {
        console.error('Error adding post:', error.message);
        alert('Failed to add post: ' + error.message);
    });
}
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        console.log(`Post ${postId} deleted.`);
        loadPosts();
    })
    .catch(error => {
        console.error('Error deleting post:', error);
        alert('Failed to delete post.');
    });
}