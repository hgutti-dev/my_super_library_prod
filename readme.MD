# 📚 My Super Library API

**My Super Library** is a RESTful API designed to manage a digital library system, allowing students and librarians to interact with books, users, and loans in a structured and efficient way.

The project follows modern backend best practices and includes a complete **CI/CD pipeline that builds and deploys the application as a Docker image**.

---

## 🚀 Main Features

### 👨‍🎓 Student Flow

- Students can **view the complete list of books** available in the library.
- Books can be **searched or filtered by**:
  - Title
  - Author
  - Genre
- Students can **view detailed information** for a selected book.
- Each book detail shows whether there are **available copies in stock**.
- If copies are available, the student can **request a book checkout**.
  - Once checked out, the **stock of the book decreases automatically**.
- Students can view **all books they have currently checked out**.
- After using a book, the student can **return it to the library**.

---

### 🧑‍🏫 Librarian Flow

- Librarians can **view all users who currently have books checked out**.
- They can **mark a book as returned**, which will:
  - Close the checkout record
  - **Increase the book stock automatically**
- Librarians are responsible for **creating and managing users**.
- When adding a new user, the following information is required:
  - First name
  - Last name
  - Email
  - Role (e.g. Student, Librarian)

---

## ⚙️ Technology Stack

- **Backend Framework:** FastAPI
- **Language:** Python
- **Database:** MongoDB
- **Containerization:** Docker
- **CI/CD:** GitHub Actions
- **Deployment:** Docker Image (automatically deployed via CI/CD)

---

## 🔄 CI/CD & Deployment

This project includes a fully automated **CI/CD pipeline**:

- On every push or pull request:
  - Tests are executed automatically
  - The Docker image is built
- On successful builds:
  - The Docker image is **published**
  - The application is **deployed automatically**

This ensures:

- Consistent environments
- Reliable deployments
- Faster development cycles

---

## 🐳 Docker Support

The application runs inside a Docker container, making it easy to deploy and scale across different environments.

Typical flow:

1. Code is pushed to the repository
2. CI pipeline runs tests
3. Docker image is built
4. Image is deployed automatically

---

## 📌 Project Goals

- Practice real-world backend architecture
- Apply clean code and layered design principles
- Implement a complete CI/CD workflow
- Build a scalable and maintainable API

---

## Check it out and use the endpoints

https://my-super-library-latest-docker.onrender.com/

## 📄 License

This project is intended for educational and personal development purposes.

---

## ✨ Author

Developed by **Herbert Gutierrez**
