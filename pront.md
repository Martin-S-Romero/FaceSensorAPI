## 🔍 Project Context

We are building a **media censorship system** in Python using OpenCV.

### Current state

* A Python class already exists that:

  * Detects **eyes** and **mouth** in images and videos.
  * Applies censorship types:

    * Blur boxes
    * Pixelated boxes
    * Black solid boxes
  * Accepts inputs from:

    * Local file path
    * Remote URL
  * Saves all processed files inside local directories.

---

## 🎯 Project Goal

Transform this into a **complete FastAPI service** running entirely inside Docker.

What the API must support:

* Upload images/videos
* Provide a URL to fetch a remote file
* Select a censorship type
* Process synchronously (images) or asynchronously (videos, optional)
* Return the censored file
* Store all input/output files persistently

---

## 🧩 Requirements for the Agent (Cascade Code)

Cascade Code should:

1. **Infer and propose a robust architecture**, scalable and modular.
2. Generate a clean folder structure, like:

   ```
   /app
     /src
       /api
       /services
       /models
       /utils
     /storage
       /input
       /output
   ```
3. Refactor or redesign the censorship class using:

   * SOLID principles
   * Separation of concerns
   * Extensible design for adding new censorship methods
4. Build FastAPI endpoints that:

   * Perform file uploads
   * Accept URLs
   * Call the censorship service
   * Return processed files
   * Do not contain business logic
5. Provide Docker integration:

   * Dockerfile (slim, optimized)
   * docker-compose with volume persistence
6. Implement file management utilities.
7. Prepare code for future scalability:

   * Optional async video processing (Celery + Redis)
   * Logging
   * Dependency injection

---

## 📦 Expected Output from Cascade Code

Cascade Code should generate:

### 1. Full architecture proposal

* Folder tree
* Responsibility of each module
* Explanation of flow

### 2. Core Python code

* Censorship service class
* Video/image handler
* File loader (from path & URL)

### 3. FastAPI modules

* `/process/image`
* `/process/video`
* `/process/url`
* Model schemas
* Router modules
* Highly decoupled logic

### 4. Docker & environment setup

* Dockerfile
* docker-compose.yml
* Volume configuration
* Production-ready notes

### 5. Future enhancements

* Async job queue
* GPU/OpenCV optimizations
* Error and edge-case handling
* CI/CD suggestions

---

## 🎛 Style Instructions for Cascade Code

* Clean, modular, production-ready code
* Strong typing (PEP 484)
* Use classes, not large scripts
* Avoid business logic inside routes
* Use small composable services
* Document functions briefly
* Generate code in a logical multi-step cascade

---

## 🟢 END OF PROMPT

If quieres, puedo generar una **versión aún más corta**, o una versión enfocada para **arrancar directamente un cascade con pasos numerados**.
