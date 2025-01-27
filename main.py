import streamlit as st
from PIL import Image

from bs_service import BSService, BSServiceConfig


image = Image.open("./asset/bs_meter.webp")

st.title("Bullshit meter!")


st.markdown("""
    This isn't your typical tool. No, this is a *super-powered bullshit detector* that can measure the amount of **corporate jargon** lurking in a text. Whether you're drafting a business proposal or just talking about the next big thing in tech, this meter will tell you how much of it is just hot air! 🌪️🔥
""")

st.image(
    image, caption="The Bullshit Meter - Gauge your content!", width=200, clamp=True
)


st.markdown(
    """
    <p>
        <a href="https://buymeacoffee.com/navicstein" target="_blank">
            <img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=navicstein&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" alt="Buy me a coffee">
        </a>
    </p>

        """,
    unsafe_allow_html=True,
)


with st.expander("Advanced Model Configuration"):
    st.info(
        "This is powered by LiteLLM, you can change the model and API key if you have a custom model like Ollama & OpenAI, see: https://docs.litellm.ai/docs/#basic-usage"
    )

    model = st.text_input("Model", value="deepseek/deepseek-chat")
    api_key = st.text_input(
        "API Key",
        value="xxxxxxxxxxxxxxx",
        help="Use your Deepseek API key or TogetherAI with the API base",
    )

    config = BSServiceConfig(model=model, api_key=api_key)

tab1, tab2 = st.tabs(["Text", "URL"])

with tab1:
    text_input = st.text_area("Paste your text here:")

    if text_input:
        total_chars = len(text_input)
        total_words = len(text_input.split())


with tab2:
    st.warning(
        "Warning: The results may not be accurate, prefer copying the contents of the website instead."
    )
    url_input = st.text_input("Enter URL:")


service = BSService(config)
if st.button("Calculate Bullshit", key="1"):
    text_or_url = text_input or url_input

    if not text_or_url:
        st.warning("Please enter some text or url")
    else:
        with st.spinner("Calculating bullshit..."):
            output = service.calculate_bullshit(text_or_url)

        st.markdown(f"### **Bullshit Score**: **{output.score}/10**")

        if output.score <= 3:
            st.success("Low Bullshit! 🌟")
        elif 4 <= output.score <= 7:
            st.warning("Moderate Bullshit! ⚠️")
        else:
            st.error("High Bullshit! 🚨")

        st.write(f"**Explanation**: {output.explanation}")


st.markdown(
    """
        <hr/>
        <footer>
            <p>Developed by Navicstein. Check out the <a href="https://github.com/steinathan/bullshitmeter" target="_blank">GitHub repository</a>.</p>
        </footer>
        """,
    unsafe_allow_html=True,
)
