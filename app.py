import os
import streamlit as st
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import tempfile

# Set up API key
DEEPGRAM_API_KEY = 'e58f982a0db66eb1c8e33be980d5f7bfcd66a546'

# Initialize client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

def transcribe_audio(audio_file, language):
    """
    Transcribe the given audio file using Deepgram API.
    """
    try:
        buffer_data = audio_file.read()
        payload = {"buffer": buffer_data}
        options = PrerecordedOptions(
            smart_format=True,
            model='general',
            language=language,
            punctuate=True,
            diarize=True
        )

        with st.spinner('Transcribing audio... This may take a few moments.'):
            response = deepgram.listen.rest.v("1").transcribe_file(
                payload, options)
            st.success('Transcription completed!')

        transcript = create_markdown_transcript(response)
        return transcript
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def create_markdown_transcript(response):
    """
    Create a markdown formatted transcript from the Deepgram response.
    """
    transcript = response.results.channels[0].alternatives[0]
    words = transcript.words

    markdown_content = "# Transcription\n\n"
    current_speaker = None
    current_paragraph = ""

    for word in words:
        if word.speaker != current_speaker:
            if current_paragraph:
                markdown_content += f"## Speaker {current_speaker}\n\n{current_paragraph.strip()}\n\n"
                current_paragraph = ""
            current_speaker = word.speaker

        current_paragraph += f"{word.punctuated_word} "

    if current_paragraph:
        markdown_content += f"## Speaker {current_speaker}\n\n{current_paragraph.strip()}\n\n"

    return markdown_content

def main():
    st.title("Audio Transcription App")
    st.write("Upload a WAV file to get its transcription")

    # File uploader
    uploaded_file = st.file_uploader("Choose a WAV file", type=['wav'])

    # Language selection
    language = st.selectbox(
        "Select language",
        options=['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ja', 'ko', 'zh'],
        format_func=lambda x: {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }[x]
    )

    if uploaded_file is not None:
        # Create a transcribe button
        if st.button("Transcribe"):
            transcription = transcribe_audio(uploaded_file, language)

            if transcription:
                # Display the transcription
                st.markdown(transcription)

                # Create download button for the transcription
                st.download_button(
                    label="Download Transcription",
                    data=transcription,
                    file_name="transcription.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
    