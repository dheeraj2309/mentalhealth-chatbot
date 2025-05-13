# Mental Health Support Chatbot

This is a Streamlit-based chatbot designed to offer empathetic support and basic mental well-being analysis. It uses Google's Generative AI (Gemini 1.5 Flash) to understand user input, analyze emotional state, and provide supportive responses, including crisis intervention steps if necessary.

## Features

*   **Empathetic Chat Interface:** A user-friendly chat window for interaction.
*   **AI-Powered Analysis:** Utilizes Google's Gemini model to analyze user messages for:
    *   Top 3 Emotions (with percentages)
    *   Overall Emotional Intensity
    *   Emotional Variability
    *   Thought Clarity
    *   Cognitive Bias Indicators
    *   Self-Perception
    *   Risk Indicators (self-harm, suicidal ideation, harm to others)
    *   Motivation and Energy Levels
    *   Social Connection
    *   Mentions of Sleep/Appetite Issues
    *   Temporal Factors (duration of state, triggers)
*   **Dynamic Response Generation:** Generates responses based on the analysis, focusing on:
    *   Acknowledging and validating emotions.
    *   Offering gentle, relevant coping suggestions (if no immediate crisis).
    *   Prioritizing safety with a crisis protocol.
*   **Crisis Intervention:** If critical risk indicators like suicidal ideation or self-harm are detected, the chatbot provides immediate safety-focused information and crisis hotline numbers.
*   **Analysis Visualization:**
    *   **Emotion Donut Chart:** Displays the top 3 detected emotions and their percentages in the sidebar.
    *   **Key Indicators Summary:** Shows a summary of overall intensity, energy levels, thought clarity, and social connection in the sidebar.
*   **Simulated Typing Effect:** Enhances user experience with a "typing" animation for bot responses.
*   **Chat History:** Remembers and displays the conversation.

## Technology Stack

*   **Python 3.10 or later**
*   **Streamlit:** For the web application interface.
*   **Google Generative AI (genai):** For language understanding and generation (Gemini 1.5 Flash model).
*   **Plotly:** For creating the emotion donut chart.
*   **Regex (re):** For parsing analysis output.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <https://github.com/dheeraj2309/mentalhealth-chatbot>
    cd <mentalhealth-chatbot>
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file with the following content:
    ```
    streamlit
    google-generativeai
    plotly
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Key Configuration (Crucial!):**
    This application uses `st.secrets` for API key management, which is the recommended way for Streamlit Cloud deployment.

    *   **For Streamlit Cloud Deployment:**
        1.  Go to your app's settings on `share.streamlit.io`.
        2.  Navigate to the "Secrets" section.
        3.  Add a new secret with the key `API_KEY` and paste your Google Generative AI API key as the value.
        The application code (`api_key = st.secrets["API_KEY"]`) will automatically pick this up.

    *   **For Local Development:**
        Streamlit looks for secrets in a `.streamlit/secrets.toml` file in your app's root directory.
        1.  Create a folder named `.streamlit` in the root of your project.
        2.  Inside `.streamlit`, create a file named `secrets.toml`.
        3.  Add your API key to `secrets.toml` like this:
            ```toml
            API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
            ```
        **IMPORTANT:** Add `.streamlit/secrets.toml` to your `.gitignore` file to prevent accidentally committing your API key to version control.

5.  **Run the Application:**
    ```bash
    streamlit run "final_chatbot - Copy.py"
    ```
    (Replace `"final_chatbot - Copy.py"` with the actual name of your Python file if different.)

## How it Works

1.  **User Input:** The user types a message into the chat interface.
2.  **Analysis:** The input is sent to the `analyze_sentiment_and_risk` function.
    *   A detailed prompt instructs the Gemini model to extract specific mental state parameters.
    *   The model returns a structured text analysis.
3.  **Data Extraction & Visualization:**
    *   Helper functions (`extract_emotion_data`, `extract_summary_points`) parse the analysis text.
    *   An emotion donut chart and key indicators are displayed in the sidebar.
4.  **Response Generation:** The analysis text is passed to the `generate_response` function.
    *   Another prompt guides the Gemini model to act as an empathetic companion.
    *   **Crisis Check:** If the analysis indicates critical risk, a safety-focused crisis response is generated.
    *   **Standard Response:** Otherwise, a supportive message is crafted, acknowledging feelings and offering gentle coping suggestions based on the analysis.
5.  **Display:** The generated response is displayed in the chat, with a typing effect for non-crisis messages.

## Disclaimer

This chatbot is for informational and emotional support purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition or mental health concerns. If you are in a crisis, please contact emergency servicesor a crisis hotline immediately.

---
