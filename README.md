# AllyAlley

## Description

AllyAlley is a social media platform designed to foster connections and friendships among users. It provides a space where users can share their photos and videos, interact with each other through likes and comments, and explore the posts of others. The platform's name, "AllyAlley," is symbolic of an alley where users can find allies, forming connections and bonds with others in the online community. This project was created for the Final Project of the free online CS50x course.

## Video Demo

[Watch the Video Demo](https://youtu.be/wYTvE2TONvc)

## Technologies Used

Built using Flask, HTML, CSS, Python, AJAX, SQLite, and JavaScript, AllyAlley offers a seamless user experience. Flask provides the framework for the web application, while HTML and CSS ensure a visually appealing and responsive design. JavaScript and AJAX are used to enhance user interactions, such as updating likes dynamically without refreshing the page. Lastly, it was deployed using the free tier of [PythonAnywhere](https://www.pythonanywhere.com/) for the demo.

## Features

- Basic user authentication - allowing users to create accounts and log in securely, they are unable to delete other users' posts/comments.
- Upload photos and videos - depending on the server, there may be upload size limits. The uploaded files are stored on the server.
- Like functionality updated dynamically using AJAX - there is no need to refresh the page to see the changes.
- Comment on users' posts - have something to say? Interact with other users by commenting on their posts.
- Delete posts and comments - change your mind? you are able to delete your own posts and comments.
- Visit users' profile pages- users can visit each other's profile pages to learn more about them and explore posts by a specific user.
- SQLite3 Database (user accounts, likes, comments) - storing/retrieval of user account information, likes, comments data.

## Project Structure
### Files
- `app.py`: Contains the main logic and routes for the Flask application. It handles HTTP requests and defines how the application responds to them.
- `helpers.py`: Includes helper functions for error handling and login requirements, enhancing the modularity of the codebase.
- `allyalley.db`: SQLite database file containing tables for users, posts, likes, and comments, ensuring data integrity through foreign key constraints.
- `schema.txt`: Contains the schema for the `allyalley.db` database for reference.
- `layout.html`: Base template for other templates to extend.
- `index.html`: Homepage displaying posts from all users, sorted with the most recent posts at the top.
- `login.html`: Login page for user authentication.
- `post.html`: View a specific post, including comments.
- `profile.html`: View a specific user's profile and posts.
- `register.html`: Register a new user.
- `upload.html`: Upload a new post, supporting video and pictures.

### Folders
- `uploads/`: Contains media files uploaded by users, renamed to a custom format including user ID and post ID for uniqueness.
- `static/`: Includes CSS, JavaScript, and static images for the application, serving non-changing content like site backgrounds and icons.
- `templates/`: Contains HTML templates for various pages as described under Files:


## Usage
Ensure that all dependencies in `requirements.txt` is installed into your Python environment before deploying. Tested with Python 3.10 and Python 3.12.
