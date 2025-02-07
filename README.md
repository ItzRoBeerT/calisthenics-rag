# Calisthenics Chatbot with Routine Generator

This repository contains a chatbot that answers questions about calisthenics and street workout. It can also generate personalized workout routines based on user requests.

## Key Features

*   **Knowledge Base:** Answers questions about calisthenics and street workout principles.
*   **Routine Generation:** Generates a PDF workout routine based on user requests.
*   **RAG (Retrieval-Augmented Generation):** Uses a PDF manual as context to enhance responses.
*   **Supabase Integration:** Uploads generated routines to a Supabase bucket.
*   **Gradio Interface:** User-friendly chat interface for interacting with the bot.

## Files

*   `custom_tools.py`: Contains a custom tool to generate workout routines as a PDF with `matplotlib`.
*   `functions.py`: Contains a function to upload generated PDFs to Supabase.
*   `main.py`: Main application file that sets up the chatbot, RAG pipeline, and Gradio interface.

## Usage

1.  **Set up Environment Variables:**
    *   Create a `.env` file and set the following environment variables:
        *   `OPENROUTER_API_KEY`: Your OpenRouter API key.
        *   `OPENROUTER_BASE_URL`: Your OpenRouter Base URL.
        *   `HELICONE_API_KEY`: Your Helicone API key.
        *   `SUPABASE_URL`: Your Supabase URL.
        *   `SUPABASE_API_KEY`: Your Supabase API key.
2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**

    ```bash
    python main.py
    ```

4.  **Access the Chatbot:**  Open your browser and navigate to the address provided by Gradio (usually `http://localhost:7860`).

## Notes

*   The `c.pdf` file contains the calisthenics manual used for RAG.
*   Generated routines are saved locally in the `./files` directory and uploaded to the `documents` bucket in your Supabase project, under the `rutines/` path.
* The agent uses the `generate_routine_pdf` tool to generate and save a pdf with a training routine, which is after uploaded to supabase.
content_copy
download
Use code with caution.
