# Library-Management-Microservices

This repository contains the implementation of a Library Management Application using a microservices architecture. 
The application is divided into three main exercises:

1. **Service Setup**  
   Implementing the basic microservices:
   - **UserService**: Handles user registration and management.
   - **BookService**: Manages book details and CRUD operations.
   - Both services are containerized using Docker and orchestrated with Docker Compose alongside a PostgreSQL database.

2. **Asynchronous Communication with RabbitMQ**  
   - Integration of RabbitMQ for asynchronous messaging between the UserService and a new BorrowService.
   - **BorrowService**: Processes borrow requests, validates data, and enforces the rule that a student cannot borrow more than five books at a time.
   - Modifications were made to the UserService to post borrow requests to a RabbitMQ channel.

3. **Deployment with Kubernetes**  
   - Conversion of the Docker Compose configuration into Kubernetes manifests using Kompose.
   - Deployment of the entire application onto a Kubernetes cluster.
   - Port forwarding was used to test the endpoints in a local development environment.
   - All Docker images are published to Docker Hub for deployment.

## Project Structure
```
Library-Management-Microservices/
├── exercise_one/
│   ├── BookService/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   ├── UserService/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   └── docker-compose.yml
├── exercise_two/
│   ├── BookService/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   ├── BorrowService/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   ├── UserService/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   └── docker-compose.yml
└── exercise_three/
      ├── BookService
      │   ├── Dockerfile
      │   ├── main.py
      │   └── requirements.txt
      ├── BorrowService
      │   ├── Dockerfile
      │   ├── main.py
      │   └── requirements.txt
      ├── UserService
      │   ├── Dockerfile
      │   ├── main.py
      │   └── requirements.txt
      ├── book_service-deployment.yaml
      ├── borrow_service-deployment.yaml
      ├── db-data-persistentvolumeclaim.yaml
      ├── db-deployment.yaml
      ├── db-service.yaml
      ├── docker-compose.yaml
      ├── env-configmap.yaml
      ├── rabbitmq-deployment.yaml
      ├── rabbitmq-service.yaml
      ├── user_service-deployment.yaml
      └── user_service-service.yaml
```

## Services Overview

### UserService
- **Purpose:** Manage user registration and details (register, update, delete).
- **Technology:** Python (based on `python:3.9-slim`), containerized with Docker.
- **Port:** 5002
- **Endpoints:**  
  - Add User  
  - Get All Users  
  - Get User by student ID  
  - Update User  
  - Delete User  
  - Borrow Request (integrated with RabbitMQ in Exercise Two)

### BookService
- **Purpose:** Manage book information (add, update, delete, retrieve books).
- **Technology:** Python, containerized with Docker.
- **Port:** 5006
- **Endpoints:**  
  - Add Book  
  - Get All Books  
  - Get Book by ID  
  - Update Book  
  - Delete Book  

### BorrowService
- **Purpose:** Process borrow requests from users via RabbitMQ.
- **Functionality:**  
  - Validates that the student and book exist (by interfacing with UserService and BookService).
  - Ensures that a student does not borrow more than five books at once.
  - Returns a list of books currently borrowed by a user.
- **Communication:** Subscribes to a RabbitMQ channel where borrow requests are posted.

### RabbitMQ
- **Role:** Enables asynchronous communication between services.
- **Configuration:**  
  - Credentials and connection details are read from a `.env` file.
  - RabbitMQ is included in the Docker Compose configuration for Exercise Two.

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Kubernetes](https://kubernetes.io/) (e.g., via Minikube or a managed cluster)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Kompose](https://kompose.io/) for converting Docker Compose files to Kubernetes manifests
- A Docker Hub account (for image publishing in the end)

### Setup Instructions

#### Exercise One: Service Setup
1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/Library-Management-Microservices.git
    cd Library-Management-Microservices/exercise_one
    ```
2. **Configure Environment**
    - Create a `.env` file with the necessary PostgreSQL connection properties (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
3. **Build and Run the Services**
    ```bash
    docker-compose up --build
    ```
4. **Testing the Endpoints**
    - Use Postman or curl to interact with the UserService (e.g., `http://localhost:5002`) and BookService (e.g., `http://localhost:5006`).

#### Exercise Two: Asynchronous Communication
1. **Set Up RabbitMQ**
    - Update the `.env` file with the RabbitMQ credentials (e.g., `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`).
    - Ensure the `docker-compose.yml` in the `exercise_two` folder includes the RabbitMQ service.
2. **Run the Services**
    ```bash
    docker-compose up --build
    ```
3. **Test Borrow Requests**
    - Send a POST request to the UserService endpoint for borrowing a book.
    - Verify that BorrowService processes the message and updates the records accordingly.
    - Confirm that a student cannot borrow more than five books simultaneously.

#### Exercise Three: Deployment with Kubernetes
1. **Convert to Kubernetes Manifests**
    - In the `exercise_three` folder, convert the Docker Compose file if needed:
      ```bash
      kompose convert -f ../exercise_two/docker-compose.yml
      ```
    - Or simply use the existing YAML files provided.
2. **Deploy to Kubernetes**
    ```bash
    kubectl apply -f .
    ```
3. **Test the Deployment**
    - Forward the necessary ports from your Kubernetes pods:
      ```bash
      kubectl port-forward <pod-name> <local-port>:<container-port>
      ```
    - Test the endpoints as described in Exercise One/Two.
