# School API

School API is a backend project designed to manage a school's users, classes, and related functionalities. It includes user authentication, lesson management, and file handling capabilities. [Here is the frontend application.](https://github.com/ilya-bondarev/school-react-app)

## Contents:

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [Contacts](#contacts)

## Features

- User registration and authentication
- Role-based access control (teachers, students)
- Class scheduling and status updates
- Real-time lesson board using WebSockets
- File upload and management for user profiles and lessons
- Token-based authentication and refresh

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Encryption**: bcrypt, JWT
- **WebSockets**: FastAPI WebSockets

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ilya-bondarev/school-api
   cd school-api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update file (`config.py`)

## Usage

1. Run the FastAPI application:
   ```bash
   uvicorn main:app --reload
   ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

### API Endpoints

- **Register a new user**: POST `/register`
- **User login**: POST `/token`
- **Refresh token**: POST `/refresh`
- **Get current user profile**: GET `/me`
- **Update user profile**: POST `/update-profile`
- **Upload profile photo**: POST `/upload-profile-photo/`
- **Get profile photo**: GET `/profile-photo/{filename}`
- **Upload lesson files**: POST `/upload`
- **List user files**: GET `/my-files`
- **Get lesson status**: GET `/lessons/status/{status_id}`
- **Create a lesson**: POST `/lessons/`
- **Update lesson status**: PUT `/lessons/{lesson_id}/status`
- **Load lesson state**: GET `/load-lesson/{lesson_id}`
- **Save lesson state**: POST `/save-lesson/{lesson_id}`

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## Contacts

If you have any questions, feel free to contact me through the following channels:
- **Telegram:** [@bondarev_i](https://t.me/bondarev_i)
- **Email:** [bondarev.ilya.dev@gmail.com](mailto:bondarev.ilya.dev@gmail.com)
- **LinkedIn:** [Bondarev Ilya](https://www.linkedin.com/in/bondarev-i/)
