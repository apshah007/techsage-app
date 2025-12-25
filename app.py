import streamlit as st
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="TechSage: Connected Intelligence",
    page_icon="🤖",
    layout="wide"
)

# --- SESSION STATE (The App's Memory) ---
if "saved_prompts" not in st.session_state:
    st.session_state.saved_prompts = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# --- Sidebar: API Key Input ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.markdown("[Get your key from Google AI Studio](https://aistudio.google.com/app/apikey)")
    
    if api_key:
        st.success("Key entered!")
    
    st.divider()
    st.markdown("### About")
    st.caption("Prototype v0.4: Final Version with Download.")

# --- Main Page Header ---
st.title("Prototype v0.4: Connected Intelligence")
st.info("Welcome! This tool helps seniors construct perfect AI prompts using the 'Three Ingredient' method.")

# --- Tabs ---
tab1, tab2 = st.tabs(["🛠️ Prompt Builder", "📚 Saved Prompts"])

# --- TAB 1: PROMPT BUILDER ---
with tab1:
    st.subheader("Let's build your request together.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**1. The Task 📋**")
        task_input = st.text_area(
            "What do you want the AI to do?",
            placeholder="Example: Write a song for my mom",
            height=150,
            key="widget_task"
        )

    with col2:
        st.markdown("**2. The Context 🎯**")
        context_input = st.text_area(
            "Who is this for? Any details?",
            placeholder="Example: Mom loves gardening and classical music...",
            height=150,
            key="widget_context"
        )

    st.markdown("**3. The Tone 🎭**")
    tone_option = st.select_slider(
        "How should the AI sound?",
        options=["Strict & Formal", "Professional", "Neutral", "Friendly", "Warm & Loving"],
        value="Friendly",
        key="widget_tone"
    )
    st.caption(f"Selected Tone: {tone_option}")

    st.divider()

    # --- BUTTON ROW ---
    b_col1, b_col2 = st.columns([1, 5])
    
    with b_col1:
        generate_btn = st.button("✨ Generate", type="primary")
    
    with b_col2:
        def clear_text():
            st.session_state.widget_task = ""
            st.session_state.widget_context = ""
            st.session_state.last_result = None
            
        st.button("🗑️ Clear Inputs", on_click=clear_text)

    # --- GENERATION LOGIC ---
    if generate_btn:
        if not api_key:
            st.error("Please enter your Google API Key in the sidebar first.")
        elif not task_input:
            st.warning("Please enter at least a Task to get started.")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # Auto-Detect Logic
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                if available_models:
                    chosen_model = next((m for m in available_models if 'flash' in m), 
                                      next((m for m in available_models if 'pro' in m), available_models[0]))
                    
                    model = genai.GenerativeModel(chosen_model)

                    full_prompt = (
                        f"You are a helpful assistant.\n"
                        f"TASK: {task_input}\n"
                        f"CONTEXT: {context_input}\n"
                        f"TONE: {tone_option}\n"
                        f"Please generate the response now."
                    )
                    
                    with st.spinner("Consulting Gemini..."):
                        response = model.generate_content(full_prompt)
                        st.session_state.last_result = response.text
                        st.session_state.last_prompt = f"{task_input} ({tone_option})"

                else:
                    st.error("No valid models found for your key.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

    # --- DISPLAY RESULTS ---
    if st.session_state.last_result:
        st.success("Gemini says:")
        st.markdown(st.session_state.last_result)
        
        if st.button("❤️ Save this result to Tab 2"):
            saved_item = {
                "title": st.session_state.last_prompt,
                "content": st.session_state.last_result,
                "context": context_input
            }
            st.session_state.saved_prompts.append(saved_item)
            st.balloons()
            st.toast("Saved to Tab 2!", icon="✅")

# --- TAB 2: SAVED PROMPTS ---
with tab2:
    st.header("Your Collection")
    
    # Check if we have any saved items
    if not st.session_state.saved_prompts:
        st.info("You haven't saved anything yet. Go to the Builder tab to create something!")
    
    else:
        # --- NEW: PREPARE DOWNLOAD FILE ---
        # We turn the list of saved items into one long text string
        download_text = "--- TECHSAGE COLLECTION ---\n\n"
        for item in st.session_state.saved_prompts:
            download_text += f"TITLE: {item['title']}\n"
            download_text += f"CONTEXT: {item['context']}\n"
            download_text += f"RESULT:\n{item['content']}\n"
            download_text += "-"*40 + "\n\n"
            
        # --- NEW: DOWNLOAD BUTTON ---
        st.download_button(
            label="📥 Download All as Text File",
            data=download_text,
            file_name="my_techsage_collection.txt",
            mime="text/plain",
            type="primary"
        )
        
        st.divider()

        # Display the items
        for i, item in enumerate(reversed(st.session_state.saved_prompts)):
            with st.expander(f"📄 {item['title']} (Saved item #{len(st.session_state.saved_prompts)-i})"):
                st.write("**Context provided:**")
                st.caption(item['context'])
                st.divider()
                st.markdown(item['content'])
                st.divider()
                if st.button("Delete this", key=f"del_{i}"):
                    st.session_state.saved_prompts.pop(len(st.session_state.saved_prompts)-1-i)
                    st.rerun()
