import streamlit as st
import requests
from pathlib import Path
from streamlit.logger import get_logger
from PIL import Image
import io
import base64

FASTAPI_BACKEND_ENDPOINT = "http://localhost:8000"

# Streamlit logger
LOGGER = get_logger(__name__)

# Streamlit App
def main():

    # Set the main dashboard page browser tab title and icon
    st.set_page_config(
        page_title="Brain Tumor Classification",
        page_icon="🧠",
    )

    # Initialize session state variables
    if "IS_IMAGE_FILE_AVAILABLE" not in st.session_state:
        st.session_state["IS_IMAGE_FILE_AVAILABLE"] = False
    if "PREDICTION_RESULT" not in st.session_state:
        st.session_state["PREDICTION_RESULT"] = None
    if "FEEDBACK_PROVIDED" not in st.session_state:
        st.session_state["FEEDBACK_PROVIDED"] = None
    if "CORRECT_LABEL" not in st.session_state:
        st.session_state["CORRECT_LABEL"] = None

    # Build the sidebar first
    with st.sidebar:
        # Check the status of backend
        try:
            backend_request = requests.get(FASTAPI_BACKEND_ENDPOINT)
            if backend_request.status_code == 200:
                st.success("Backend online ✅")
            else:
                st.warning("Problem connecting 😭")
        except requests.ConnectionError as ce:
            LOGGER.error(ce)
            LOGGER.error("Backend offline 😱")
            st.error("Backend offline 😱")

    st.write("# Brain Tumor Classification! 🧠")
    st.write("""
    ## Introduction
    This MLOps project aims to classify brain tumors using MRI images. 
    Please upload a brain MRI image to get started.
    """)

    # Image upload section
    uploaded_image = st.file_uploader("Upload a Brain MRI Image", type=["jpg", "jpeg"])

    # Check if client has provided an input image file
    if uploaded_image:
        st.write('Preview Image')
        image = Image.open(uploaded_image)
        st.image(image, caption='Uploaded Image', use_column_width=False, width=300)
        st.session_state["IS_IMAGE_FILE_AVAILABLE"] = True

    # Predict button
    predict_button = st.button('Predict')

    if predict_button and uploaded_image:
        # Convert image to JPEG format in memory
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)

        # Send the image to the FastAPI server for prediction
        files = {"file": ("image.jpg", image_buffer, "image/jpeg")}
        response = requests.post(f"{FASTAPI_BACKEND_ENDPOINT}/predict/", files=files)

        if response.status_code == 200:
            result = response.json()
            prediction = result['Prediction']

            # Decode the base64 images
            inference_image = Image.open(io.BytesIO(base64.b64decode(result['Inference'])))
            boundaries_image = Image.open(io.BytesIO(base64.b64decode(result['Boundaries'])))
            st.session_state["PREDICTION_RESULT"] = {
                "prediction": prediction,
                "inference_image": inference_image,
                "boundaries_image": boundaries_image
            }
            st.session_state["FEEDBACK_PROVIDED"] = None
            st.session_state["CORRECT_LABEL"] = None

        elif response.status_code == 400:
            result = response.json()
            st.error(result['error'])
            retry_button = st.button('Retry')
            if retry_button:
                st.session_state["IS_IMAGE_FILE_AVAILABLE"] = False  # Reset image availability flag
                st.experimental_rerun()  # Rerun the app to allow re-uploading
            
        else:
            st.write("Error: Could not get a prediction.")

    # Display prediction results and feedback section if available
    if st.session_state["PREDICTION_RESULT"]:
        prediction_result = st.session_state["PREDICTION_RESULT"]
        st.write(f"Prediction: {prediction_result['prediction']}")
        col1, col2 = st.columns(2)
        with col1:
            st.image(prediction_result["inference_image"], caption='Explanation', use_column_width=False, width=300)
        with col2:
            st.image(prediction_result["boundaries_image"], caption='Marked Boundaries', use_column_width=False, width=300)

        if st.session_state["FEEDBACK_PROVIDED"] is None:
            st.write("### Are you happy with the results?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Yes'):
                    st.session_state["FEEDBACK_PROVIDED"] = "yes"
                    st.experimental_rerun()
            with col2:
                if st.button('No'):
                    st.session_state["FEEDBACK_PROVIDED"] = "no"
                    st.experimental_rerun()

        elif st.session_state["FEEDBACK_PROVIDED"] == "yes":
            st.success("Thank you for your feedback!")
            exit_button = st.button('Exit')
            if exit_button:
                st.session_state["IS_IMAGE_FILE_AVAILABLE"] = False  # Reset image availability flag
                st.session_state["PREDICTION_RESULT"] = None  # Clear prediction results
                st.session_state["FEEDBACK_PROVIDED"] = None  # Clear feedback state
                st.session_state["CORRECT_LABEL"] = None  # Clear correct label
                st.experimental_rerun()  # Rerun the app to allow re-uploading

        elif st.session_state["FEEDBACK_PROVIDED"] == "no":
            st.write("### What should the correct label be?")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button('Glioma', disabled=st.session_state["CORRECT_LABEL"] is not None):
                    st.session_state["CORRECT_LABEL"] = "Glioma"
                    st.experimental_rerun()
            with col2:
                if st.button('Meningioma', disabled=st.session_state["CORRECT_LABEL"] is not None):
                    st.session_state["CORRECT_LABEL"] = "Meningioma"
                    st.experimental_rerun()
            with col3:
                if st.button('No Tumor', disabled=st.session_state["CORRECT_LABEL"] is not None):
                    st.session_state["CORRECT_LABEL"] = "No Tumor"
                    st.experimental_rerun()
            with col4:
                if st.button('Pituitary', disabled=st.session_state["CORRECT_LABEL"] is not None):
                    st.session_state["CORRECT_LABEL"] = "Pituitary"
                    st.experimental_rerun()
            exit_button = st.button('Exit')

            if exit_button:
                st.session_state["IS_IMAGE_FILE_AVAILABLE"] = False  # Reset image availability flag
                st.session_state["PREDICTION_RESULT"] = None  # Clear prediction results
                st.session_state["FEEDBACK_PROVIDED"] = None  # Clear feedback state
                st.session_state["CORRECT_LABEL"] = None  # Clear correct label
                st.experimental_rerun()  # Rerun the app to allow re-uploading

        if st.session_state["CORRECT_LABEL"]:
            st.success(f"Feedback recorded: {st.session_state['CORRECT_LABEL']}")

    if not uploaded_image or (uploaded_image and not st.session_state["IS_IMAGE_FILE_AVAILABLE"]):
        st.info("Please upload an image to proceed.")

if __name__ == "__main__":
    main()