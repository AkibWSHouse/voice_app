import streamlit as st
import asyncio
from deepgram import Deepgram

# --- Configuration ---
# Your Deepgram API key.
# For local development: create a .streamlit/secrets.toml file in your project root
# and add DEEPGRAM_API_KEY = "YOUR_API_KEY_HERE"
# For Streamlit Cloud: add this as a secret in your app's settings on the cloud dashboard.
try:
    DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]
except KeyError:
    st.error(
        "Deepgram API Key not found. Please set it in "
        "`.streamlit/secrets.toml` (for local) or via Streamlit Cloud secrets."
    )
    st.stop() # Stop the app if the key is not found, as it's essential.

# Initialize Deepgram client.
# This client handles communication with the Deepgram API.
dg_client = Deepgram(DEEPGRAM_API_KEY)

# --- Transcription Function ---
async def transcribe_microphone_audio(audio_data_bytesio):
    """
    Transcribes audio data received from Streamlit's microphone input
    using the Deepgram API.

    Args:
        audio_data_bytesio: A BytesIO object containing the audio data
                            from st.audio_input.

    Returns:
        The transcribed text as a string, or None if an error occurs.
    """
    try:
        # Prepare the audio source for Deepgram.
        # st.audio_input typically provides WebM format data.
        source = {
            'buffer': audio_data_bytesio.getvalue(), # Extract raw bytes from BytesIO
            'mimetype': "audio/webm" # Specify the MIME type of the audio data
        }

        st.info("Sending audio to Deepgram for transcription... This may take a moment.")

        # Send the audio for transcription.
        # The method call has been updated to directly call 'prerecorded'
        # as it appears to be the function itself in your Deepgram SDK version.
        response = await dg_client.transcription.prerecorded(
            source,
            {
                "smart_format": True,  # Enhances readability (punctuation, capitalization)
                "model": "nova-2",     # Using a highly accurate model
                "language": "en-US"    # Specify the language of the audio
            }
        )

        # Extract the transcribed text from the Deepgram response.
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript

    except Exception as e:
        # Catch and display any errors during the transcription process.
        st.error(f"Error during transcription: {e}")
        return None

# --- Streamlit Application Layout ---
def main():
    """
    Sets up the Streamlit application interface.
    """
    # Configure the Streamlit page title and icon.
    st.set_page_config(page_title="Microphone Voice-to-Text Transcriber", page_icon="🎤")

    st.title("🎤 Voice-to-Text Transcriber with Microphone Input")
    st.write("Record your voice using the microphone below and get an instant transcription.")

    st.markdown("---") # A horizontal line for separation

    # Streamlit widget to capture audio from the user's microphone.
    audio_bytes = st.audio_input(
        "Click 'Record' to start, then 'Stop' when you're done:",
        help="Make sure your microphone is enabled and working."
    )

    # Check if audio has been recorded by the user.
    if audio_bytes is not None:
        st.subheader("Recorded Audio Playback:")
        # Display a player for the recorded audio.
        # The format is typically 'audio/webm' for st.audio_input.
        st.audio(audio_bytes, format="audio/webm")

        # Button to trigger the transcription process.
        if st.button("Transcribe Recorded Audio", use_container_width=True):
            # Run the asynchronous transcription function within Streamlit's context.
            with st.spinner("Transcribing your audio... Please wait."):
                # asyncio.run is used to execute the async Deepgram call.
                transcript = asyncio.run(transcribe_microphone_audio(audio_bytes))

                if transcript:
                    st.success("Transcription Complete!")
                    st.subheader("Your Transcript:")
                    # Display the final transcribed text.
                    st.info(transcript)
                else:
                    st.warning("Transcription failed or returned no text. Please try recording again.")
    else:
        st.info("Ready to record! Record your voice above to get started.")

    st.markdown("---") # Another horizontal line
    st.markdown(
        "Built with ❤️ using [Streamlit](https://streamlit.io/) and "
        "[Deepgram's Speech-to-Text API](https://deepgram.com/)."
    )

# Entry point for the Streamlit application.
if __name__ == "__main__":
    main()
