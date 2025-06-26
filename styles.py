def inject_css():
    css = """
    <style>
    /* Label acima do st.radio, st.selectbox, etc */
    label[data-testid="stWidgetLabel"] > div p {
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    /* Itens dentro do st.radio */
    div[data-baseweb="radio"] label {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* Tamanho das abas (st.tabs) */
    button[data-baseweb="tab"] p {
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }
    
    </style>
    """
    import streamlit as st
    st.markdown(css, unsafe_allow_html=True)
