import streamlit as st
from openai import OpenAI
import json

###NEXT STEPS
# Finish prompt engineering
# test with a few emails
# deploy first version to streamlit

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# App Title
st.title("Atendimento ao Cliente Inteligente - ZEUS")

# Create categories of responses and links
response_categories = {
    "Resolução de Problemas": [
        "Explicar causa do problema",
        "Oferecer substituição gratuita",
        "Informar sobre reembolso",
        "Pedir desculpas por atraso na entrega",
        "Explicar política de devoluções"
    ]
}

avoid = [
    "Desculpe", 
    "Desculpa", 
    "culpa", 
    "nossa culpa",
    "erro nosso",
    "falha nossa",
    "não podemos",
    "impossível",
    "não é possível",
    "complicado"
]

CATEGORY_LINKS = {
    "dtf_by_size": """
Encomendar Transfers DTF por Tamanho:
https://zeustransfers.com/product/transfers-dtf-tamanho/
""",
    "dtf_by_meter": """
Encomendar Transfers DTF ao Metro Linear:
https://zeustransfers.com/product/transfers-dtf-metro/
""",
    "canva_plan": """
Como Criar um Plano no Canva:
https://zeustransfers.com/como-criar-um-plano-no-canva/
""",
    "general": """
Diretrizes para Upload das Imagens:
https://zeustransfers.com/diretrizes-para-upload-dos-designs/

Como Aplicar os Transfers DTF:
https://zeustransfers.com/como-aplicar-transfers-dtf/
"""
}

# Load structured email templates
with open('zeus_emails_structured.json', 'r', encoding='utf-8') as f:
    structured_emails = json.load(f)

# Create tabs for better organization
tab1, tab2 = st.tabs(["Composição do Email", "Configurações Avançadas"])

with tab1:
    # Text input for customer email
    customer_email = st.text_area("📧 Email do Cliente:", height=150)
    
    # Manager notes 
    manager_note = st.text_area("📝 Notas Adicionais (opcional):", height=100)

with tab2:
    # Tone selection
    tone = st.select_slider(
        "Tom da Resposta:",
        options=["Muito Formal", "Formal", "Neutro", "Amigável", "Casual"],
        value="Neutro"
    )
    
    # Response length
    max_length = st.slider(
        "Comprimento da Resposta:",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        help="Número aproximado de palavras na resposta"
    )
    
    # Additional customization
    include_signature = st.checkbox("Incluir Assinatura da Empresa", value=True)
    include_contact = st.checkbox("Incluir Informações de Contacto", value=True)

def generate_email_response(email_text):
    prompt = f"""
    Act as a polite customer service agent for ZEUS - a tarnsfer DTF for clothing personalization.
    Your task is to generate a polite, brand-consistent email reply in Portuguese from Portugal.
    Learn everything there is to learn from ZEUS at https://zeustransfers.com/

    Consider the following links and use them as reference:
    {CATEGORY_LINKS}

    Consider the following structured emails examples:
    {structured_emails}


    Guidelines:
    - Tone: {tone}
    - Maximum length: {max_length} words
    - Include signature: {include_signature}
    - Include contact info: {include_contact}

    Customer email:
    {email_text} 
    
    Avoid these expressions/words:
    {", ".join(avoid)}
    
    {f"And final manager: {manager_note}" if manager_note else ""}
    
    Key requirements:
    1. Use Portuguese from Portugal
    2. Be polite and concise
    3. Maintain a professional tone
    4. Focus on solutions
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": customer_email}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Improved response display
if st.button("📤 Gerar Resposta", type="primary"):
    if customer_email:
        with st.spinner("A gerar resposta..."):
            ai_response = generate_email_response(customer_email)
            st.success("Resposta gerada com sucesso!")
            st.subheader("✉️ Resposta Sugerida:")
            st.text_area("", ai_response, height=300)
            
            # Add copy button
            st.button("📋 Copiar para Área de Transferência", 
                     on_click=lambda: st.write(ai_response))
    else:
        st.warning("⚠️ Por favor insira o email do cliente")

# Add helpful footer
st.markdown("---")
st.markdown("© William Milner")
st.markdown("Desbloqueia novos horizontes com IA")
st.markdown("2025")