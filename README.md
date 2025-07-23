# Docu-Flow AI

![Docu-Flow AI Banner](https://placehold.co/1200x400/0056b3/ffffff?text=Docu-Flow+AI&font=poppins)

**An intelligent document processing platform that automates the extraction, analysis, and summarization of information from your documents using a powerful AI pipeline.**

---

## 🚀 Overview

Docu-Flow AI is a modern web application designed to solve the time-consuming challenge of manual document analysis. Users can upload PDF documents, and the system will automatically process them through a sophisticated backend pipeline. This pipeline extracts text, creates vector embeddings for semantic understanding, and uses a generative AI model to produce high-quality summaries and key insights.

This project serves as a comprehensive demonstration of building a scalable, serverless, AI-powered application with a modern tech stack.

## ✨ Key Features

-   **Seamless Document Upload**: A user-friendly, drag-and-drop interface for uploading PDF documents.
-   **Asynchronous Processing Pipeline**: The UI remains fast and responsive while complex AI tasks are handled in the background.
-   **AI-Powered Text Extraction**: Automatically performs OCR and text extraction on uploaded documents.
-   **Intelligent Analysis & Summarization**: Leverages a powerful generative model to generate concise summaries and extract key insights.
-   **Vector-Based Indexing**: Creates vector embeddings of document content for future semantic search capabilities.
-   **Intuitive Dashboard**: View all your documents, track their processing status, and access the final results in a clean, organized interface.
-   **Detailed Results View**: See the extracted data, AI-generated summary, and other metadata for each processed document.

## 🛠️ Tech Stack

This project is built with a modern, serverless-first technology stack:

-   **Framework**: [Next.js](https://nextjs.org/) (React)
-   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
-   **File Uploads**: [UploadThing](https://uploadthing.com/)
-   **Database (Relational)**: [Neon](https://neon.tech/) (Serverless Postgres)
-   **ORM**: [Prisma](https://www.prisma.io/)
-   **Vector Database**: [Pinecone](https://www.pinecone.io/)
-   **AI Orchestration**: [LangChain](https://js.langchain.com/)


## 🏗️ System Architecture

The system is designed around an asynchronous, event-driven architecture.

1.  **Client-Side**: The Next.js frontend handles user interaction. Files are uploaded directly to UploadThing storage.
2.  **Backend API**: Upon successful upload, an automated notification triggers a Next.js API route.
3.  **Processing Pipeline**: This API route initiates the LangChain-orchestrated pipeline:
    -   The document is loaded, and text is extracted.
    -   The text is cleaned, split into chunks, and converted into vector embeddings using the Gemini model.
    -   These embeddings are indexed and stored in the Pinecone vector database.
    -   A final call is made to the Gemini model to generate a summary and insights.
4.  **Data Storage**: File metadata and the final analysis results are stored in the Neon Postgres database via Prisma.

## ⚙️ Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

-   Node.js (v18 or later)
-   npm, yarn, or pnpm
-   Git

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/kent0309/docu-flow-ai-smart.git](https://github.com/kent0309/docu-flow-ai-smart.git)
    cd docu-flow-ai-smart
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Set up environment variables:**
    Create a file named `.env` in the root of the project and add the following environment variables. You will need to get these keys from their respective platforms.

    ```env
    # Database
    DATABASE_URL="your_neon_postgres_connection_string"

    # UploadThing
    UPLOADTHING_SECRET="your_uploadthing_secret_key"
    UPLOADTHING_APP_ID="your_uploadthing_app_id"

    # Pinecone
    PINECONE_API_KEY="your_pinecone_api_key"
    PINECONE_ENVIRONMENT="your_pinecone_environment"

    # Google Gemini
    GOOGLE_API_KEY="your_google_ai_studio_api_key"
    ```

4.  **Push the database schema:**
    Run the following command to sync your Prisma schema with your Neon database.
    ```sh
    npx prisma db push
    ```

5.  **Run the development server:**
    ```sh
    npm run dev
    ```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 📖 Usage

1.  Navigate to the **Upload** page.
2.  Drag and drop a PDF file or click to select one from your computer.
3.  Once the upload is complete, you will be redirected to the **Dashboard**.
4.  Your document will appear in the list with a "Processing" status.
5.  Once the backend pipeline is finished, the status will update to "Completed".
6.  Click on the document to view the detailed results, including the AI-generated summary and extracted data.
