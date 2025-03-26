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

# Initialize structured_emails as an empty dictionary
structured_emails = {}

# Load structured email templates
try:
    with open('zeus_emails_structured.json', 'r', encoding='utf-8') as f:
        loaded_emails = json.load(f)
        if isinstance(loaded_emails, dict):
            structured_emails = loaded_emails
        else:
            st.warning("⚠️ O arquivo de templates não está no formato correto.")
except FileNotFoundError:
    st.warning("⚠️ Arquivo de templates de email não encontrado. Continuando sem exemplos estruturados.")
except json.JSONDecodeError:
    st.warning("⚠️ Erro ao decodificar o arquivo de templates. Continuando sem exemplos estruturados.")
except Exception as e:
    st.warning(f"⚠️ Erro ao carregar templates: {str(e)}. Continuando sem exemplos estruturados.")

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["Composição do Email", "Configurações Avançadas", "Templates e Referências"])

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
    include_links = st.checkbox("Incluir Links Relevantes", value=True)

with tab3:
    st.markdown("### 📚 Templates e Referências")
    
    # Templates section
    st.subheader("📋 Templates Disponíveis")
    if structured_emails and len(structured_emails) > 0:
        template_categories = list(structured_emails.keys())
        selected_category = st.selectbox(
            "Selecione uma categoria:",
            ["Nenhuma"] + template_categories
        )
        
        if selected_category != "Nenhuma":
            category_data = structured_emails[selected_category]
            
            # Show template
            st.markdown("#### Template Base:")
            st.text_area("", category_data["template"], height=200)
            
            # Show examples
            st.markdown("#### Exemplos de Uso:")
            for i, example in enumerate(category_data["examples"], 1):
                with st.expander(f"Exemplo {i}"):
                    st.markdown("**Email do Cliente:**")
                    st.text_area("", example["customer"], height=100)
                    st.markdown("**Resposta:**")
                    st.text_area("", example["response"], height=200)
    else:
        st.info("Nenhum template disponível no momento.")
    
    # Reference links section
    st.subheader("🔗 Links de Referência")
    for category, info in PRODUCT_INFO.items():
        with st.expander(f"🔹 {info['name']}"):
            st.write(info['description'])
            for link_name, link_url in info['links'].items():
                st.markdown(f"- [{link_name.replace('_', ' ').title()}]({link_url})")

def generate_email_response(email_text):
    # Build context from structured emails
    context = []
    if structured_emails and len(structured_emails) > 0:
        context.append("Available Templates and Examples:")
        for category, data in structured_emails.items():
            context.append(f"\nCategory: {category}")
            context.append("Template:")
            context.append(data["template"])
            context.append("\nExamples:")
            for example in data["examples"]:
                context.append(f"\nCustomer: {example['customer'][:100]}...")
                context.append(f"Response: {example['response'][:100]}...")

    # Add product information context
    context.append("\nProduct Information:")
    for category, info in PRODUCT_INFO.items():
        context.append(f"\n{info['name']}:")
        context.append(info['description'])
        for link_name, link_url in info['links'].items():
            context.append(f"- {link_name}: {link_url}")

    prompt = f"""
    Act as a professional customer service agent for ZEUS Transfers, a company specializing in DTF transfers for clothing personalization.
    Your task is to generate a helpful, informative, and brand-consistent email reply in Portuguese from Portugal.

    Company Context:
    ZEUS Transfers specializes in high-quality DTF transfers, offering both size-based and meter-based options.
    We provide comprehensive design services and support for our customers.

    Reference Information:
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
    8. Use similar structure and tone as the reference templates when applicable
    9. Consider the context from similar customer inquiries in the examples
    10. Follow the same format and style as the example responses in the reference templates
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