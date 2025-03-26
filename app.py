import streamlit as st
from openai import OpenAI
import json

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# App Title and Description
st.title("Atendimento ao Cliente Inteligente - ZEUS")
st.markdown("""
### 🤖 Assistente Virtual ZEUS
Este assistente ajuda a gerar respostas profissionais e informativas para os clientes da ZEUS Transfers.
""")

# Define comprehensive product information and links
PRODUCT_INFO = {
    "dtf_transfers": {
        "name": "Transfers DTF",
        "description": "Transfer digital direto para tecido (DTF) de alta qualidade",
        "links": {
            "by_size": "https://zeustransfers.com/product/transfers-dtf-tamanho/",
            "by_meter": "https://zeustransfers.com/product/transfers-dtf-metro/",
            "application": "https://zeustransfers.com/como-aplicar-transfers-dtf/",
            "guidelines": "https://zeustransfers.com/diretrizes-para-upload-dos-designs/"
        }
    },
    "design_services": {
        "name": "Serviços de Design",
        "description": "Criação e personalização de designs",
        "links": {
            "canva_guide": "https://zeustransfers.com/como-criar-um-plano-no-canva/",
            "design_help": "https://zeustransfers.com/designs/"
        }
    },
    "support": {
        "name": "Suporte",
        "description": "Informações e ajuda",
        "links": {
            "faq": "https://zeustransfers.com/faq/",
            "contact": "https://zeustransfers.com/contacto/"
        }
    }
}

# Define response categories with specific use cases
RESPONSE_CATEGORIES = {
    "Informações de Produtos": [
        "Informações sobre Transfers DTF",
        "Guias de Aplicação",
        "Especificações Técnicas",
        "Opções de Personalização"
    ],
    "Suporte Técnico": [
        "Problemas de Aplicação",
        "Dúvidas sobre Design",
        "Questões de Qualidade",
        "Ajustes e Correções"
    ],
    "Vendas e Encomendas": [
        "Informações de Preço",
        "Opções de Encomenda",
        "Prazos de Entrega",
        "Métodos de Pagamento"
    ],
    "Pós-Venda": [
        "Devoluções",
        "Garantias",
        "Reclamações",
        "Feedback"
    ]
}

# Words to avoid in responses
AVOID_WORDS = [
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

# Load structured email templates
try:
    with open('zeus_emails_structured.json', 'r', encoding='utf-8') as f:
        structured_emails = json.load(f)
except FileNotFoundError:
    st.warning("⚠️ Arquivo de templates de email não encontrado. Continuando sem exemplos estruturados.")
    structured_emails = {}

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["Composição do Email", "Configurações Avançadas", "Informações de Referência"])

with tab1:
    # Text input for customer email
    customer_email = st.text_area("📧 Email do Cliente:", height=150)
    
    # Response category selection
    selected_categories = []
    for category, options in RESPONSE_CATEGORIES.items():
        st.subheader(f"🔹 {category}")
        category_selections = st.multiselect(
            "Selecione os tópicos relevantes:",
            options,
            key=f"category_{category}"
        )
        selected_categories.extend(category_selections)
    
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
    include_links = st.checkbox("Incluir Links Relevantes", value=True)

with tab3:
    st.markdown("### 📚 Informações de Referência")
    for category, info in PRODUCT_INFO.items():
        with st.expander(f"🔹 {info['name']}"):
            st.write(info['description'])
            for link_name, link_url in info['links'].items():
                st.markdown(f"- [{link_name.replace('_', ' ').title()}]({link_url})")

def generate_email_response(email_text):
    # Build context from selected categories
    context = []
    for category in selected_categories:
        for product_category, info in PRODUCT_INFO.items():
            if category.lower() in info['name'].lower():
                context.append(f"Category: {info['name']}")
                for link_name, link_url in info['links'].items():
                    context.append(f"- {link_name}: {link_url}")

    prompt = f"""
    Act as a professional customer service agent for ZEUS Transfers, a company specializing in DTF transfers for clothing personalization.
    Your task is to generate a helpful, informative, and brand-consistent email reply in Portuguese from Portugal.

    Company Context:
    ZEUS Transfers specializes in high-quality DTF transfers, offering both size-based and meter-based options.
    We provide comprehensive design services and support for our customers.

    Relevant Information:
    {chr(10).join(context)}

    Guidelines:
    - Tone: {tone}
    - Maximum length: {max_length} words
    - Include signature: {include_signature}
    - Include contact info: {include_contact}
    - Include relevant links: {include_links}

    Customer email:
    {email_text}
    
    Avoid these expressions/words:
    {", ".join(AVOID_WORDS)}
    
    {f"Additional notes: {manager_note}" if manager_note else ""}
    
    Key requirements:
    1. Use Portuguese from Portugal
    2. Be polite, professional, and solution-oriented
    3. Always include relevant links to our website when applicable
    4. Focus on providing clear, actionable information
    5. Maintain a positive and helpful tone
    6. Structure the response logically with clear sections if needed
    7. Include specific product recommendations when relevant
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