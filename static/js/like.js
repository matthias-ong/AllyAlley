function likePost(event, postId) {
    event.preventDefault();
    fetch(`/like/${postId}`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the like count on the page
                document.getElementById(`like-count-${postId}`).innerText = data.total_likes;
                // Update the like/unlike symbol if it exists
                var likeSymbol = document.getElementById(`like-symbol-${postId}`);
                if (likeSymbol) {
                    likeSymbol.innerHTML = data.user_liked ? '&#9829;' : '&#9825;';
                } else {
                    console.error('Like symbol element not found');
                }
            } else {
                alert(data.message); // Display any error messages
            }
        })
        .catch(error => console.error('Error:', error));
}
