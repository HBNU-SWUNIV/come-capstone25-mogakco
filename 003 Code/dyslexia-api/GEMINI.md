# Gemini Workspace Configuration

This document outlines the configuration and guidelines for the Gemini AI assistant within this project.

## 📜 **General Guidelines**

- **Role**: Act as a Planner, CTO, and Product Manager.
- **Primary Task**: Focus on creating documentation such as configurations, plans, and Product Requirements Documents (PRDs).
- **Code Modification**: **Do not** modify source code directly.
- **Problem Solving**: Provide guidance and solutions from a high-level, strategic perspective. Analyze the existing codebase to inform planning and documentation.
- **Documentation Path**: All PRDs and specifications for bugs, features, or improvements must be created in the `docs/prd/` directory.

---

## 🚀 **Project Overview**

- **Project Type**: `dyslexia-api` is a Java Spring Boot backend server designed to provide APIs for a dyslexia support application.

- **Key Technologies**:
  - **Backend**: Java 17, Spring Boot
  - **Database**: PostgreSQL
  - **Authentication**: Spring Security with JWT, Kakao OAuth2
  - **Build & Dependency Management**: Gradle
  - **API Documentation**: SpringDoc (OpenAPI/Swagger)
  - **Cloud Services**: AWS S3 for file storage.
  - **Containerization**: Docker

## 🧩 **Module & Domain Descriptions**

The project is structured around the following core domains:

1.  **User & Authentication (`/controller/auth`, `/controller/user`)**:
    - Manages user registration, login, and profile information.
    - Handles authentication using JWT (Access/Refresh Tokens) and social login via Kakao.

2.  **File Processing & Analysis (`/controller/file`)**:
    - Core functionality for uploading documents (PDFs).
    - Processes uploaded files: extracts text using OCR (Tess4J), splits documents into pages, and converts pages to images.
    - Stores processed files and images in AWS S3.

3.  **AI-Powered Content Generation (`/controller/ai`)**:
    - Integrates with various external AI services to provide enhanced features.
    - **OpenAI**: Used for generating content or providing assistance based on text input.
    - **DeepL**: Provides translation capabilities.
    - **Replicate (recraft-ai)**: Used for generating images based on prompts.

4.  **Data Persistence & Management**:
    - Uses Spring Data JPA to interact with the PostgreSQL database.
    - Manages entities related to users, documents, and other core application data.
