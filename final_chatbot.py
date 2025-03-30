import streamlit as st
import google.generativeai as genai
import json
import re
import plotly.graph_objects as go
import time # For simulating typing effect

"""Everything just feels so heavy lately, like I'm wading through thick fog just to get through the day. It's been like this for weeks, maybe longer? I don't even know anymore. My thoughts are all tangled up, can't seem to focus on anything properly. Tried talking to a friend the other day but just ended up staring blankly, couldn't even form the words, so I cancelled. Easier to just stay in bed, honestly, though sleep isn't really happening either - mostly just lying there feeling... nothing? Or maybe everything, all at once? It's exhausting. Sometimes I just wish it would all stop, you know? Like, permanently. That thought keeps popping up and it scares me, but part of me feels like it might be the only way to get some quiet from the noise in my head. Is that crazy? I don't know what to do."""
# --- Secrets and API Key Configuration ---
# try:
#     with open("secrets.json") as s:
#         secrets = json.load(s)
#     api_key = secrets['API_KEY']
#     genai.configure(api_key=api_key)
# except FileNotFoundError:
#     st.error("`secrets.json` not found. Please create this file with your API key.")
#     st.stop()
# except KeyError:
#     st.error("`API_KEY` not found in `secrets.json`.")
#     st.stop()
# except Exception as e:
#     st.error(f"Error loading secrets or configuring API: {e}")
#     st.stop()
genai.configure(api_key="AIzaSyAZHbulqRXuZaI0Ajmr3XU71dhIc1zDgTU")
# --- LLM Initialization ---
# Consider adding error handling for model initialization
try:
    # Use the same model for both analysis and response for simplicity
    llm_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Failed to initialize the Generative Model: {e}")
    st.stop()

# --- Analysis Function (Keep the strict format output) ---
def analyze_sentiment_and_risk(user_input, model):
    # (Keep the analyze_sentiment_and_risk function exactly as defined in the previous version)
    # ... (ensure it returns the structured analysis string or an error string) ...
    try:
        prompt = f"""Role: You are a mental health analysis assistant trained to deeply evaluate emotional well-being from user input. Your goal is to analyze the user's message and provide detailed, objective parameters that describe their mental state. Analyze the following message to deduce objective parameters defining the user's mental state. Provide output ONLY under the following categories exactly as listed, with clear values:
1. Emotional State:
   - Dominant Emotion: [e.g., Sadness, Joy, Anger, Anxiety, Fear, Numbness, Contentment, Overwhelm]
   - Emotion Intensity: [1-10, where 1 is very low and 10 is extremely high]
   - Emotional Variability: [Stable or Fluctuating]
2. Cognitive State:
   - Thought Clarity: [Clear or Disorganized]
   - Cognitive Bias Indicators: [List any detected, e.g., Catastrophizing, Overgeneralization, Negative Filtering, None Detected]
   - Self-Perception: [Positive, Neutral, Negative, Mixed]
3. Behavioral Indicators:
   - Risk Indicators: [Explicitly state: "Self-harm mentioned", "Suicidal ideation mentioned", "Harmful intent towards others mentioned", or "No specific risk indicators detected"]
   - Motivation and Energy Levels: [High, Moderate, Low, Very Low]
   - Social Connection: [Connected, Isolated, Seeking Connection, Ambivalent]
   - Mentions of Sleep/Appetite Issues: [Yes or No]
4. Temporal Factors:
   - Duration of Emotional State: [Likely Short-term, Likely Long-term, Unclear]
   - Presence of Recent Triggering Events: [Mentioned, Implied, Not Mentioned]

Input Message: {user_input}

Provide a detailed breakdown following the structure above precisely. Do not add any introductory or concluding sentences outside this structure."""
        response = model.generate_content(prompt)
        if not response.text or "Emotional State:" not in response.text:
             print(f"Warning: Unexpected analysis format received:\n{response.text}")
             return "Error: Analysis generation failed to produce expected format."
        return response.text
    except Exception as e:
        print(f"Error during analysis: {e}")
        # Provide a more specific error if possible, e.g., API errors
        return f"Error: Could not analyze the message due to an internal issue ({type(e).__name__})."


# --- Response Generation Function (Using principles, not explicit suggestions) ---
def generate_response(sentiment_analysis, model):
    # (Keep the generate_response function exactly as defined in the previous version)
    # ... (ensure it takes analysis, checks for risk, generates response, and handles errors) ...
    critical_risk_indicated = False
    if sentiment_analysis and isinstance(sentiment_analysis, str):
       if re.search(r'Risk Indicators:.*(suicidal|self-harm|self harm|kill myself|end my life|hurt myself)', sentiment_analysis, re.IGNORECASE):
           critical_risk_indicated = True

    try:
        prompt = f"""Role: Empathetic Mental Health Support Companion.

        Task: Generate a warm, natural, and supportive response to a user based on the provided internal analysis of their message. Prioritize safety and genuine care. If no immediate crisis is detected, include gentle, relevant coping suggestions derived from the analysis.

        **Internal Analysis Context (FOR YOUR INFORMATION ONLY - DO NOT MENTION THIS STRUCTURE OR ITS LABELS TO THE USER):**
        {sentiment_analysis}

        **Response Requirements:**

        1.  **Crisis Protocol (Highest Priority):**
            *   **Condition:** Check if `critical_risk_indicated` is True (based on 'Risk Indicators' in the analysis).
            *   **Action:** If condition met, **immediately** generate a response focused *only* on safety: Express calm, serious concern; emphasize help availability; state urgency; provide specific crisis resources (988, 741741, local emergency); reiterate care and urge immediate action. **STOP** - provide no other advice.

        2.  **Standard Response (If No Crisis Detected):**
            *   **Acknowledge & Validate:** Start by warmly acknowledging the core emotion(s) and intensity from the analysis. Validate these feelings compassionately.
            *   **Reflect Understanding:** Subtly weave in understanding related to other analysis points (like energy, thoughts, social connection) without naming categories, showing you grasp the situation.
            *   **Generate Relevant Support:**
                *   Identify the primary challenge(s) highlighted by the analysis (e.g., high intensity, low energy, disorganized thoughts, isolation).
                *   Based *only* on these identified challenges from the analysis, generate 1-2 simple, actionable suggestions aimed at providing gentle relief or coping *relevant to those specific challenges*.
                *   Ensure the generated suggestions are appropriate for the analyzed energy level and cognitive state (e.g., low-effort ideas for low energy).
                *   Frame suggestions as gentle, optional possibilities ("Perhaps consider...", "Sometimes it can help to...", "One small thing might be...").
            *   **Encourage:** End with encouragement for self-compassion and suggest considering further support (professional or trusted person) if feelings persist.

        **Tone:** Consistently warm, compassionate, empathetic, non-judgmental. Natural, human-like language. Avoid clinical jargon.

        **Constraint:** **Never** reveal or reference the internal analysis structure or its specific labels in your response to the user. Use the analysis *only* to inform the content and tone.

        Generate the response now."""
        response = model.generate_content(prompt)
        return response.text, critical_risk_indicated # Return risk flag as well

    except Exception as e:
        print(f"Error during response generation: {e}")
        return f"Error: Could not generate a response due to an internal issue ({type(e).__name__}).", critical_risk_indicated # Return flag even on error

# --- Helper Function to Extract Intensity ---
def extract_intensity(analysis_text):
    if not analysis_text or "Error:" in analysis_text:
        return None
    try:
        match = re.search(r"Emotion Intensity:\s*(\d+)", analysis_text)
        if match:
            return int(match.group(1))
        else:
            # Try matching if the number is directly after colon without space
            match = re.search(r"Emotion Intensity:(\d+)", analysis_text)
            if match:
                return int(match.group(1))
    except Exception as e:
        print(f"Error parsing intensity: {e}")
    return None # Return None if not found or error

# --- Helper Function to Create Gauge Chart ---
def create_gauge_chart(intensity_value):
    if intensity_value is None or not (1 <= intensity_value <= 10):
         # Return a placeholder or empty figure if no valid intensity
         fig = go.Figure()
         fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=30, b=10),
            annotations=[dict(
                text="Intensity N/A",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5
            )]
         )
         return fig

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = intensity_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Analyzed Intensity", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "rgba(0,0,0,0)"}, # Transparent bar, steps define color
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#cccccc",
            'steps': [
                {'range': [0, 4], 'color': 'lightgreen'},
                {'range': [4, 7], 'color': 'yellow'},
                {'range': [7, 10], 'color': 'coral'}],
            'threshold': { # Optional: Add a marker line
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8.5 # Example threshold for high intensity
                }
            }))
    fig.update_layout(
        height=200, # Adjust size as needed
        margin=dict(l=20, r=20, t=30, b=10), # Adjust margins
        font=dict(color="#333333", family="Arial, sans-serif")
        )
    return fig

# --- Streamlit App ---
st.set_page_config(layout="centered", page_title="Support Chat")

st.title(" M Mental Health Support Chat") # Add an icon to title

# --- Sidebar for Visualization ---
st.sidebar.header("Current State Indicator")
gauge_placeholder = st.sidebar.empty() # Placeholder for the chart

# Initialize or update gauge based on the latest intensity in session state
latest_intensity = st.session_state.get("latest_intensity", None)
gauge_placeholder.plotly_chart(create_gauge_chart(latest_intensity), use_container_width=True)


# --- Main Chat Interface ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.latest_intensity = None # Initialize intensity state

# Display prior chat messages
for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else " M" # Simple Emojis
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("How are you feeling today?"):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # --- Assistant Turn ---
    with st.chat_message("assistant", avatar=" M"):
        analysis_text = ""
        response_text = ""
        critical_risk_flag = False

        # 1. Analysis Step
        with st.spinner("Analyzing..."):
            analysis_text = analyze_sentiment_and_risk(prompt, llm_model)
            # Update intensity in session state for sidebar
            st.session_state.latest_intensity = extract_intensity(analysis_text)
            # Rerun script slightly delayed to update sidebar BEFORE showing response
            time.sleep(0.1) # Small delay allows rerun for gauge update
            # Update gauge directly without full rerun (more efficient)
            gauge_placeholder.plotly_chart(create_gauge_chart(st.session_state.latest_intensity), use_container_width=True)


        # Check for analysis errors
        if "Error:" in analysis_text:
            response_text = f"Sorry, I encountered an issue during analysis: {analysis_text}"
            critical_risk_flag = False # Assume no risk if analysis failed badly
            st.error(response_text) # Display error clearly
        else:
            # 2. Response Generation Step (if analysis OK)
            response_placeholder = st.empty() # Placeholder for streaming effect
            response_placeholder.markdown(" M Thinking...") # Initial thinking message
            try:
                # Use a spinner for the generation phase
                # with st.spinner("Crafting response..."): # Alternative to thinking message
                response_text, critical_risk_flag = generate_response(analysis_text, llm_model)

                # Simulate typing effect (optional)
                full_response_md = ""
                # Add alert prefix if needed
                alert_prefix = "❗️ **Safety Alert:**\n\n" if critical_risk_flag else ""
                base_response_text = response_text.replace("Error: ","") # Clean potential error prefix
                display_text = alert_prefix + base_response_text

                for chunk in display_text.split():
                    full_response_md += chunk + " "
                    response_placeholder.markdown(full_response_md + "▌") # Typing cursor
                    time.sleep(0.05) # Adjust speed
                response_placeholder.markdown(display_text) # Final message

            except Exception as e:
                response_text = f"Sorry, I encountered an error while generating the response: {e}"
                st.error(response_text)
                critical_risk_flag = False # Reset flag on generation error

    # 3. Add assistant message to history (only if not an error displayed above)
    if response_text and "Sorry, I encountered an issue during analysis" not in response_text and "error while generating the response" not in response_text :
         # Store the raw response text, display handles formatting
         st.session_state.messages.append({"role": "assistant", "content": response_text, "risk": critical_risk_flag})


# Optional: Add a footer or disclaimer
st.markdown("---")
st.caption("Disclaimer: This chatbot is for informational and emotional support purposes only and does not substitute professional medical advice, diagnosis, or treatment. In case of a crisis, please contact emergency services or a crisis hotline immediately.")