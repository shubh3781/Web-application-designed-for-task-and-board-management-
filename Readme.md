# Task Management Web Application

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Session Management](#session-management)
- [Error Handling](#error-handling)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

This project is a task management web application built using Flask. Users can create boards, add tasks, assign tasks to users, and track the status of tasks. Google Cloud services like Datastore and Firebase are used for user data storage and authentication. It allows team collaboration by inviting users to boards and assigning tasks to specific members.

## Features

- **User Authentication**: User login is managed via Google Firebase authentication.
- **Task Management**: Create tasks, assign tasks to users, and mark them as complete.
- **Board Management**: Create, update, and delete boards for project/task tracking.
- **Invite Users to Boards**: Invite users to collaborate on boards and assign tasks to them.
- **Track Task Completion**: Visualize active, completed, and daily completed tasks for each board.
- **Google Cloud Integration**: Store board and task data in Google Cloud Datastore.

## Requirements

- Python 3.x
- Flask
- Google Cloud SDK
- Google Cloud Datastore
- Google Firebase

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/task-management-flask-app.git
   cd task-management-flask-app
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Google Cloud**

   - Ensure that you have Google Cloud SDK installed and authenticated.
   - Create a Google Cloud project and enable Datastore and Firebase.
   - Add your project configuration to `constants.py` for project-specific settings like `PROJECT_NAME` and Firebase configuration.

6. **Run the Flask Application**

   ```bash
   python app.py
   ```

## Usage

1. **Sign In**: Users are authenticated using Google Firebase, with session data stored securely using Flask session management.
2. **Create Boards**: Users can create boards to organize tasks for different projects.
3. **Add Tasks**: Tasks can be created and added to specific boards. Tasks have due dates and times.
4. **Assign Tasks**: Users can assign tasks to collaborators on the board.
5. **Mark Tasks as Completed**: Tasks can be marked as complete, and the system tracks when and by whom the task was completed.
6. **Invite Users**: Collaborators can be invited to boards by email, allowing them to view and manage tasks.

## API Endpoints

- **`GET /`**: Root route that displays the user's boards and handles Google Firebase authentication.
- **`POST /add_board_to_db`**: Creates a new board for the logged-in user.
- **`POST /add_task`**: Adds a new task to a board.
- **`POST /mark_completed`**: Marks a task as completed.
- **`POST /edit_task`**: Updates an existing task's details.
- **`POST /delete_task`**: Deletes a task from a board.
- **`POST /assign_task`**: Assigns a task to a specific user.
- **`POST /invite_user`**: Invites a user to a board.
- **`POST /remove_user`**: Removes a user from a board and unassigns their tasks.

## Session Management

Session data is managed using Flask's session object and cookies. Each session stores:
- `name`: The name of the authenticated user.
- `email`: The email address of the authenticated user.

Session management is integrated with Firebase for authentication, ensuring a secure and scalable user management process.

## Error Handling

- **Authentication Errors**: If a user is not authenticated or their Firebase token is invalid, an error message is displayed.
- **Task and Board Management Errors**: Proper validation ensures that tasks and boards are not duplicated and that required fields are provided.
- **File Upload Errors**: Errors during task or board creation are handled with clear messages to the user.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Google Cloud](https://cloud.google.com/) for storage, Datastore, and Firebase authentication.
- [Werkzeug](https://werkzeug.palletsprojects.com/) for utilities related to security and routing.
