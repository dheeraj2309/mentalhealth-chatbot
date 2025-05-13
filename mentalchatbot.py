import streamlit as st
import google.generativeai as genai
import json
import re
import plotly.graph_objects as go
import time # For simulating typing effect


api_key = st.secrets["API_KEY"]

genai.configure(api_key=api_key)

try:
    llm_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Failed to initialize the Generative Model: {e}")
    st.stop()

def analyze_sentiment_and_risk(user_input, model):
    try:
        prompt = f"""Role: You are a mental health analysis assistant trained to deeply evaluate emotional well-being from user input. Your goal is to analyze the user's message and provide detailed, objective parameters that describe their mental state. Analyze the following message to deduce objective parameters defining the user's mental state. Provide output ONLY under the following categories exactly as listed, with clear values:
1. Emotional State:
   - Top 3 Emotions: [Emotion1: percentage%, Emotion2: percentage%, Emotion3: percentage%] # e.g., Anxiety: 60%, Sadness: 30%, Other: 10% (Sum should ideally be 100%)
   - Overall Intensity: [1-10, where 1 is very low and 10 is extremely high]
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

        if not response.text or "Top 3 Emotions:" not in response.text:
             print(f"Warning: Unexpected analysis format received (missing 'Top 3 Emotions'):\n{response.text}")
             return "Error: Analysis generation failed to produce expected emotion format."
        return response.text

    except Exception as e:
        print(f"Error during analysis: {e}")
        return f"Error: Could not analyze the message due to an internal issue ({type(e).__name__})."

def generate_response(sentiment_analysis, model):
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

def extract_emotion_data(analysis_text):
    """Parses the 'Top 3 Emotions' line and returns a dict."""
    emotion_data = {}
    if not analysis_text or "Error:" in analysis_text:
        return None
    try:
        match = re.search(r"Top 3 Emotions:\s*\[([^\]]+)\]", analysis_text, re.IGNORECASE)
        if match:
            emotions_str = match.group(1)
            parts = emotions_str.split(',')
            for part in parts:
                part = part.strip()
                emotion_match = re.match(r"(.+):\s*(\d+)%?", part)
                if emotion_match:
                    emotion_name = emotion_match.group(1).strip()
                    percentage = int(emotion_match.group(2))
                    emotion_data[emotion_name] = percentage
            return emotion_data if emotion_data else None # Return None if empty
    except Exception as e:
        print(f"Error parsing emotion data: {e}\nText: {analysis_text}")
    return None

def extract_summary_points(analysis_text):
    """Extracts key points for sidebar display."""
    if not analysis_text or "Error:" in analysis_text:
        return "Analysis data not available."

    points = {}
    patterns = {
        "Overall Intensity": r"Overall Intensity:\s*([\d]+)",
        "Energy Levels": r"Motivation and Energy Levels:\s*([\w\s]+)",
        "Thought Clarity": r"Thought Clarity:\s*([\w\s]+)",
        "Social Connection": r"Social Connection:\s*([\w\s]+)"
    }

    summary_lines = []
    for key, pattern in patterns.items():
        match = re.search(pattern, analysis_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if key == "Overall Intensity":
                value += "/10"
            summary_lines.append(f"**{key}:** {value}")

    if not summary_lines:
        return "Could not extract summary points."

    return "\n".join(f"- {line}" for line in summary_lines)


def create_emotion_donut_chart(emotion_data):
    if not emotion_data or not isinstance(emotion_data, dict):
        fig = go.Figure()
        fig.update_layout(
            height=250, # Adjust size
            margin=dict(l=20, r=20, t=30, b=10),
            title=dict(text="Emotion Analysis Unavailable", font=dict(color="#333333")), # Darker text
            annotations=[dict(text=" ", showarrow=False)] # Prevent default text
        )
        return fig

    labels = list(emotion_data.keys())
    values = list(emotion_data.values())

    # Define colors - you can customize these
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'] # Default Plotly colors

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, # Increase hole size slightly
                                marker_colors=colors[:len(labels)],
                                pull=[0.05] * len(labels), # Slightly pull segments
                                hoverinfo='label+percent', textinfo='percent', # Show percent on segments
                                textfont_size=14, # Make percentage text larger
                                insidetextorientation='radial' # Orient text
                               )])
    fig.update_layout(
        height=250, # Adjust size
        margin=dict(l=20, r=20, t=40, b=10), # Adjust margins for title
        title=dict(text="Analyzed Emotion Snapshot", font=dict(size=16, color="#ffffff")), # Darker title
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5), # Horizontal legend below
        font=dict(color="#333333"), # Default darker font color for legend etc.
        showlegend=True # Ensure legend is visible
    )
    return fig


# --- Streamlit App ---
st.set_page_config(layout="centered", page_title="Support Chat")

st.title(" Mental Health Support Chat")

# --- Sidebar for Visualization & Summary ---
st.sidebar.header("Analysis Snapshot")
chart_placeholder = st.sidebar.empty()
summary_placeholder = st.sidebar.empty()

# Initialize session state for analysis data
if "latest_analysis_summary" not in st.session_state:
    st.session_state.latest_analysis_summary = None
if "latest_emotion_data" not in st.session_state:
    st.session_state.latest_emotion_data = None

# Display initial placeholder message if no analysis yet
if st.session_state.latest_emotion_data is None:
     chart_placeholder.info("Emotion analysis will appear here.")
     summary_placeholder.info("Key indicators will appear here.")
else:
    # Display chart and summary if data exists
    chart_placeholder.plotly_chart(
        create_emotion_donut_chart(st.session_state.latest_emotion_data),
        use_container_width=True
    )
    summary_placeholder.markdown("#### Key Indicators:")
    summary_placeholder.markdown(st.session_state.latest_analysis_summary)


# --- Main Chat Interface ---
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "🤖" # Changed bot icon
    with st.chat_message(message["role"], avatar=avatar_icon):
        # Display alert for past risk messages if needed
        if message["role"] == "assistant" and message.get("risk", False):
             st.warning(message["content"]) # Use warning box for risk response
        else:
            st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("How are you feeling today?"):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # --- Assistant Turn ---
    with st.chat_message("assistant", avatar="🤖"): # Changed bot icon
        analysis_text = ""
        response_text = ""
        critical_risk_flag = False

        # 1. Analysis Step
        with st.spinner("Analyzing..."):
            analysis_text = analyze_sentiment_and_risk(prompt, llm_model)

            # Extract data for sidebar AFTER analysis
            st.session_state.latest_emotion_data = extract_emotion_data(analysis_text)
            st.session_state.latest_analysis_summary = extract_summary_points(analysis_text)

            # Update sidebar immediately
            chart_placeholder.plotly_chart(
                create_emotion_donut_chart(st.session_state.latest_emotion_data),
                use_container_width=True
            )
            if st.session_state.latest_analysis_summary:
                summary_placeholder.markdown("#### Key Indicators:")
                summary_placeholder.markdown(st.session_state.latest_analysis_summary)
            else: # Handle case where summary extraction failed
                 summary_placeholder.warning("Could not display key indicators.")


        # Check for analysis errors before proceeding
        if "Error:" in analysis_text:
            response_text = f"Sorry, I encountered an issue during analysis: {analysis_text}"
            critical_risk_flag = False # Assume no risk if analysis failed badly
            st.error(response_text) # Display error clearly in chat
        else:
            # 2. Response Generation Step (if analysis OK)
            response_placeholder = st.empty()
            response_placeholder.markdown("🤖 Thinking...") # Initial thinking message
            try:
                response_text, critical_risk_flag = generate_response(analysis_text, llm_model)

                # Simulate typing effect (optional)
                full_response_md = ""
                base_response_text = response_text.replace("Error: ","") # Clean potential error prefix

                # Display based on risk flag
                if critical_risk_flag:
                    # Use st.warning directly in the chat message for risk
                    response_placeholder.warning(f"{base_response_text}")
                    # Store the text without markdown formatting for history
                    response_text_for_history = base_response_text
                else:
                    # Normal typing effect
                    for chunk in base_response_text.split():
                        full_response_md += chunk + " "
                        response_placeholder.markdown(full_response_md + "▌")
                        time.sleep(0.05)
                    response_placeholder.markdown(base_response_text) # Final normal message
                    response_text_for_history = base_response_text

            except Exception as e:
                response_text = f"Sorry, I encountered an error while generating the response: {e}"
                st.error(response_text)
                response_text_for_history = response_text # Store error for history
                critical_risk_flag = False # Reset flag

    # 3. Add assistant message to history (only if not an error displayed above)
    # Store the generated text and the risk flag
    if response_text and "Sorry, I encountered an issue during analysis" not in response_text :
         st.session_state.messages.append({
            "role": "assistant",
            "content": response_text_for_history, # Store clean text
            "risk": critical_risk_flag
         })

# Optional: Footer/Disclaimer
st.markdown("---")
st.caption("Disclaimer: This chatbot is for informational and emotional support purposes only...") # Keep 