import streamlit as st
import os
import logging
import datetime
import time
from ai_handlers import AIHandler
from utils import load_env_variables, log_tokens, DBOracle
import google.generativeai as genai
import docx

# Configure logger
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

# Database credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = "UATGVPDB.ITRANS.INT/GVPUAT2"
# os.getenv("DB_DSN")


# Initialize database connection
db = DBOracle(DB_USER, DB_PASSWORD, DB_DSN)

# Initialize AI handler
ollama_base_url = "http://uatml1.itrans.int:11434/"
ollama_model = "llama3.1"
ai_handler = AIHandler(ollama_base_url, ollama_model)

# Streamlit page configuration
st.set_page_config(
    page_title="IntelliTrans Meeting Summary",
    page_icon="assets/favico.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar: Template Selection
uploaded_file = None
meeting_type = None


with st.sidebar:
    st.image("assets/intellitrans_note_transparents.png", use_container_width=True)

    st.subheader("1. Input Transcript")
    input_method = st.radio("Choose input method", ["Upload File", "Paste Text"])
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload file:", type=["txt", "docx"])
    else:
        transcript_text = st.text_area("Paste transcript here:", height=200)

    st.subheader("2. Select Meeting Type")

    try:
        templates = db.fetch_templates()
        if templates:
            template_names = [template["name"] for template in templates]
            meeting_type = st.selectbox("Choose Template", options= template_names, index=template_names.index("General Meeting"))
            selected_prompt = next(
                (t["prompt"] for t in templates if t["name"] == meeting_type), ""
            )
            st.info(selected_prompt, icon="ℹ️")
        else:
            st.error("No templates found in the database.")
            logging.warning("No templates found.")
    except Exception as e:
        st.error("Error fetching templates.")
        logging.error("Error fetching templates", exc_info=True)

    if meeting_type == "Custom Prompt":
        custom_prompt = st.text_area("Enter your custom prompt:")
        if not custom_prompt.strip():
            st.warning("Please provide a custom prompt.")

    # st.subheader("3. Choose AI Model")
    # model_choice = st.radio("Select Processing Engine", ["Ollama", "Gemini Pro"], index=0)

    model_choice = "Ollama"

# Main Content Area
# st.title("Meeting Summary Generator")
if st.button("Generate Summary"):
    start_time = time.time()
    transcript = ""
    custom_prompt = ""

    if input_method == "Upload File" and uploaded_file:
        if uploaded_file.type == "text/plain":
            transcript = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            transcript = "\n".join(p.text for p in doc.paragraphs)
        else:
            st.error("Unsupported file format.")
            logging.warning("Unsupported file uploaded.")
    else:
        transcript = transcript_text.strip()

    if transcript:
        with st.spinner("Processing your transcript..."):
            prompt = custom_prompt if meeting_type == "Custom Prompt" else selected_prompt
            try:
                if model_choice == "Gemini Pro":
                    response = ai_handler.generate_summary_gemini(transcript, prompt)
                else:
                    response = ai_handler.generate_summary_ollama(transcript, prompt)
                input_tokens, output_tokens = log_tokens(transcript, response)
                duration = round(time.time() - start_time, 2)

                # Save to session state (for feedback)
                st.session_state.update(
                    {
                        "transcript": transcript,
                        "response": response,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "duration": duration,
                        "user_id" : int(time.time()),
                    }
                )       

                # st.subheader("📋 Meeting Summary")
                # st.write(response)

                st.text_area("📋 Generated Meeting Summary", value=response, height=300)

                db.log_entry(
                    event="Meeting Summary",
                    model=model_choice,
                    input_message=st.session_state.get("transcript", ""),
                    output_message=st.session_state.get("response", ""),
                    input_tokens=st.session_state.get("input_tokens", 0),
                    output_tokens=st.session_state.get("output_tokens", 0),
                    duration=st.session_state.get("duration", 0),
                    error_message=None,
                    user_id=st.session_state.get("user_id", ""),
                    user_rating= None,
                    # st.session_state.get("user_rating", None),
                    user_feedback= "",
                    # st.session_state.get("user_feedback", ""),
                    created_date=datetime.datetime.now(),
                    custom_prompt=custom_prompt if meeting_type == "Custom Prompt" else None,
                )


                st.download_button("Download Summary", response, "summary.txt", "text/plain")

                # col1, col2 = st.columns([1, 1])

                # with col1:
                #     st.download_button("Download Summary", response, "summary.txt", "text/plain")

                # with col2:
                #     if st.button("Reset"):
                #         for key in st.session_state.keys():
                #             del st.session_state[key]
                #         st.experimental_rerun()

                logging.info("Summary generated successfully.")
            except Exception as e:
                st.error("Error generating summary.")
                logging.error("Error during summary generation", exc_info=True)
    else:
        st.warning("Please provide a transcript.")


def handle_feedback_submission():
    try:
        # Generate a unique logid (you can replace this with a specific value if required)
        logid = int(time.time())  # Example: Use a timestamp as a unique identifier

        # Log the feedback into the IntelliNotes_Feedback table
        feedback_logged = db.log_feedback(
            logid=logid,
            user_id=st.session_state.get("user_id", ""),  # Replace with the actual user_id if dynamic user management is implemented
            user_feedback=st.session_state.get("user_feedback", ""),
            user_rating=st.session_state.get("user_rating", 3),
            created_date=datetime.datetime.now(),
        )

        if feedback_logged:
            st.success("Thank you for your feedback!")
            logging.info(f"Feedback submitted successfully. LogID: {logid}")
            reset_feedback_fields()  # Reset session state after successful submission
        else:
            st.error("Failed to submit feedback. Please try again.")
            logging.warning(f"Failed to log feedback. LogID: {logid}")

    except Exception as e:
        st.error("Error saving feedback.")
        logging.error("Error during feedback logging", exc_info=True)


def reset_feedback_fields():
    """Resets all feedback-related session state fields."""
    st.session_state["user_feedback"] = ""  # Reset feedback text
    st.session_state["user_rating"] = 3  # Reset slider to default value (e.g., 3)


# Feedback UI
st.subheader("Feedback")
st.text_area("Enter feedback:", key="user_feedback", value="")  # Feedback input
# st.slider("Rate the summary quality:", 1, 5, 3, key="user_rating")  # Rating slider

# Submit Button
st.button("Submit Feedback", on_click=handle_feedback_submission)
