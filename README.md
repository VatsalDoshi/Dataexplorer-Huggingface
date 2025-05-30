# Dataset Management & Impact Assessment App

## Overview

This project is a full-stack web application for managing datasets, following datasets, creating dataset combinations, and assessing dataset impact. It features a FastAPI backend and a React frontend with Redux for state management.

## Features

- **Authentication**: Secure user registration and login with JWT tokens.
- **Dataset Management**: Browse, follow, and unfollow datasets.
- **Dataset Combinations**: Create and manage combinations of datasets.
- **Impact Assessment**: Assess dataset impact using naive or advanced methods.
- **Version History**: View dataset version history.
- **Responsive UI**: Clean and intuitive user interface.

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL

## Installation

### Backend

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the backend directory with the following variables:
     ```
     DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
     SECRET_KEY=<your-secret-key>
     ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Backend

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. The backend will be available at `http://localhost:8000`.

### Frontend

1. Start the React development server:
   ```bash
   npm start
   ```

2. The frontend will be available at `http://localhost:3000`.

## Usage

- **Register/Login**: Use the `/register` and `/login` pages to create an account or log in.
- **Browse Datasets**: Visit `/datasets` to see all available datasets.
- **Follow Datasets**: Click the "Follow" button on a dataset to follow it.
- **Create Combinations**: Go to `/combinations/create` to create a new dataset combination.
- **Assess Impact**: Visit `/impact` to assess the impact of datasets using naive or advanced methods.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. 