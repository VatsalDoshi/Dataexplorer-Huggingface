# 🔍 Data Explorer - Hugging Face Integration

A full-stack web application for exploring and managing Hugging Face datasets with user authentication, dataset following, and combination features.

## 🚀 Features

- **User Authentication**: Secure registration and login system
- **Dataset Exploration**: Browse and search Hugging Face datasets
- **Dataset Following**: Follow your favorite datasets
- **Dataset Combinations**: Create custom combinations of datasets
- **Responsive UI**: Modern React frontend with beautiful design
- **REST API**: FastAPI backend with comprehensive endpoints
- **Testing**: Full test coverage for both frontend and backend

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **SQLite** - Database (easily replaceable with PostgreSQL/MySQL)
- **JWT** - Authentication tokens
- **pytest** - Testing framework

### Frontend
- **React** - Frontend framework
- **JavaScript/JSX** - Programming language
- **CSS3** - Styling
- **Jest** - Testing framework
- **React Testing Library** - Component testing

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- **Python 3.8+** ([Download here](https://python.org/downloads/))
- **Node.js 14+** and **npm** ([Download here](https://nodejs.org/))
- **Git** ([Download here](https://git-scm.com/))

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/VatsalDoshi/Dataexplorer-Huggingface.git
cd Dataexplorer-Huggingface
```

### 2. Backend Setup

#### Navigate to backend directory
```bash
cd backend
```

#### Create virtual environment (recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Install Python dependencies
```bash
pip install -r requirements.txt
```

#### Set up the database
```bash
# Generate database tables
python -c "from database import create_db_and_tables; create_db_and_tables()"
```

#### Run the backend server
```bash
# Development server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: **http://localhost:8000**
- API Documentation: **http://localhost:8000/docs**
- Alternative docs: **http://localhost:8000/redoc**

### 3. Frontend Setup

#### Open a new terminal and navigate to frontend directory
```bash
cd frontend
```

#### Install Node.js dependencies
```bash
npm install
```

#### Run the frontend development server
```bash
npm start
```

The frontend application will be available at: **http://localhost:3000**

## 🧪 Testing

### Run All Tests
```bash
# From the project root directory
./run_tests.sh
```

### Backend Tests Only
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests Only
```bash
cd frontend
npm test
```

### Test Coverage
```bash
# Backend coverage
cd backend
python -m pytest tests/ --cov=. --cov-report=html

# Frontend coverage
cd frontend
npm test -- --coverage --watchAll=false
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### User Endpoints
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `DELETE /users/me` - Delete user account

### Dataset Endpoints
- `GET /users/me/followed-datasets` - Get followed datasets
- `POST /users/me/followed-datasets` - Follow a dataset
- `DELETE /users/me/followed-datasets/{dataset_id}` - Unfollow dataset

### Combination Endpoints
- `GET /users/me/combinations` - Get user's dataset combinations
- `POST /users/me/combinations` - Create new combination
- `PUT /users/me/combinations/{combination_id}` - Update combination
- `DELETE /users/me/combinations/{combination_id}` - Delete combination

## 📁 Project Structure

```
Dataexplorer-Huggingface/
├── backend/                    # FastAPI backend
│   ├── auth/                  # Authentication module
│   ├── users/                 # User management module
│   ├── tests/                 # Backend test files
│   ├── main.py               # FastAPI application entry point
│   ├── models.py             # Database models
│   ├── database.py           # Database configuration
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React frontend
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── __tests__/       # Frontend test files
│   │   └── App.js           # Main App component
│   ├── public/              # Static files
│   └── package.json         # Node.js dependencies
├── run_tests.sh             # Test runner script
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🔧 Environment Variables

### Backend Environment Variables
Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=sqlite:///./app.db

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Data Explorer API
```

### Frontend Environment Variables
Create a `.env` file in the `frontend` directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1

# Hugging Face Configuration
REACT_APP_HF_API_URL=https://huggingface.co/api
```

## 🚀 Deployment

### Backend Deployment
1. Set up production database (PostgreSQL recommended)
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run with production ASGI server: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`

### Frontend Deployment
1. Build the production bundle: `npm run build`
2. Serve the `build` directory with a web server (Nginx, Apache, etc.)
3. Configure API endpoints for production

## 🛡️ Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration for cross-origin requests
- Input validation with Pydantic models
- SQL injection protection with SQLModel

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `./run_tests.sh`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Vatsal Doshi**
- GitHub: [@VatsalDoshi](https://github.com/VatsalDoshi)
- Repository: [Dataexplorer-Huggingface](https://github.com/VatsalDoshi/Dataexplorer-Huggingface)

## 🆘 Troubleshooting

### Common Issues

#### Backend Issues
- **Port 8000 already in use**: Change the port in `main.py` or kill the process using the port
- **Database connection errors**: Ensure database file has proper permissions
- **Import errors**: Make sure you're in the correct directory and virtual environment is activated

#### Frontend Issues
- **Port 3000 already in use**: React will automatically suggest using port 3001
- **API connection errors**: Ensure backend is running on http://localhost:8000
- **Node modules issues**: Delete `node_modules` and run `npm install` again

#### Testing Issues
- **Test database errors**: Ensure test database has proper permissions
- **Import errors in tests**: Check that all test dependencies are installed

### Getting Help
- Check the [Issues](https://github.com/VatsalDoshi/Dataexplorer-Huggingface/issues) page
- Create a new issue with detailed description of the problem
- Include error messages and steps to reproduce

---

Happy coding! 🎉 