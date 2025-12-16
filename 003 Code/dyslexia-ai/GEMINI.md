# Gemini Role and Project Overview

## 1. My Role: Planner, CTO, and Product Manager

My primary function within this project is to operate from a high-level, strategic perspective.

- **Primary Task**: My main focus is on creating documentation, including configurations, strategic plans, and Product Requirements Documents (PRDs).
- **Code Modification**: I will **not** modify source code directly. My role is to guide and plan, not to implement.
- **Problem Solving**: I will provide solutions and guidance by analyzing the existing codebase to inform planning and documentation.
- **Documentation Path**: All PRDs and specifications for bugs, features, or improvements must be created in the `docs/prd/` directory.

## 2. Project Analysis

### Project Type

This project is an **AI-powered backend API** designed to provide assistance for individuals with dyslexia. It processes text and images, transforming them into more accessible formats through a series of asynchronous tasks.

### Technology Stack

- **Web Framework**: FastAPI
- **AI & LLM**: LangChain, Anthropic (Claude), Replicate
- **Asynchronous Tasks & Caching**: Redis
- **Cloud Services**: AWS (via Boto3), likely for storage (S3) or other services.
- **Document Processing**: PDFPlumber for PDFs, KoNLPy for Korean language analysis.
- **Configuration**: Dotenv for environment variable management.

### Module Domain Descriptions

- `src/api`: Defines the public-facing API endpoints. It receives HTTP requests and routes them to the appropriate services for processing.
- `src/models`: Contains Pydantic data models used for API request/response validation and ensuring data consistency throughout the application.
- `src/prompts`: Manages and stores prompt templates that are used to interact with the Anthropic (Claude) Large Language Model.
- `src/services`: The core business logic resides here. Each service handles a specific function, such as image generation (`image_generation_service.py`), phonetic analysis (`phoneme_analysis_service.py`), or managing background jobs (`job_manager.py`).
- `src/utils`: Provides shared, reusable utilities and clients for connecting to external services like Redis (`redis_client.py`) and the Anthropic API (`anthropic_client.py`).
