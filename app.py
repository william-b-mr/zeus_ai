import streamlit as st
from openai import OpenAI
import json
import random
from datetime import datetime

### Current state: app runs well, a bit slow, the repsonse just became better now that we increased the number of examples
### But it seems to be overly complicated, we should try to simplify it
### Next steps:
### Implement option with 200/500 characters
### Test more examples
### Understand all app logic
### Look for unused variables
### Look for simplifications 



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

def get_structured_emails(json_data, category=None, n=8):
    """
    Extract and format examples from structured emails.
    
    Args:
        json_data: Dictionary containing structured emails
        category: Optional category to filter examples
        n: Number of examples to return
    
    Returns:
        Formatted string of examples
    """
    examples = []

    if category and category in json_data:
        examples = json_data[category]["examples"]
    else:
        # Randomly pull from all categories
        for c in json_data:
            examples.extend(json_data[c]["examples"])
    
    # Limit to top N
    selected = random.sample(examples, min(len(examples), n))
    
    # Format them
    return "\n\n".join([f"CLIENTE: {ex['customer']}\nZEUS: {ex['response']}" for ex in selected])

def get_time_based_greeting():
    """
    Determine the appropriate greeting based on the current time.
    
    Returns:
        str: The appropriate greeting (Bom dia, Boa tarde, or Boa noite)
    """
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "Bom dia"
    elif 12 <= current_hour < 19:
        return "Boa tarde"
    else:
        return "Boa noite"

def generate_email_response(
    email_text,
    tone,
    max_length,
    include_signature,
    include_contact,
    include_links,
    manager_note=None,
    structured_emails=None
):
    # Get relevant examples
    examples = get_structured_emails(structured_emails) if structured_emails else ""
    
    # Get time-based greeting
    greeting = get_time_based_greeting()
    
    prompt = f"""
    Act as a professional customer service agent for ZEUS Transfers, a company specializing in DTF transfers for clothing personalization.
    Your task is to generate a helpful, informative, and brand-consistent email reply in Portuguese from Portugal.

    Company Context:
    ZEUS Transfers specializes in high-quality DTF transfers, offering both size-based and meter-based options.
    We provide comprehensive design services and support for our customers.

    Here are some example conversations to guide your response style and format:

    {examples}

    Guidelines:
    - Tone: {tone}
    - Maximum length: {max_length} words
    - Include signature: {include_signature}
    - Include contact info: {include_contact}
    - Include relevant links: {include_links}
    - Start your response with: {greeting}

    Customer email:
    {email_text}
    
    Avoid these expressions/words:
    {", ".join(AVOID_WORDS)}
    
    {f"Additional notes: {manager_note}" if manager_note else ""}
    
    Key requirements:
    1. Use Portuguese from Portugal
    2. Be polite, professional, and solution-oriented
    3. Always include relevant links to our website when applicable
    4. Include specific product recommendations when relevant
    5. Follow the same format and style as the example responses above
    6. When addressing quality issues, always explain the technical reasons and provide solutions
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": email_text}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Improved response display
if st.button("📤 Gerar Respostas", type="primary"):
    if customer_email:
        with st.spinner("A gerar respostas..."):
            # Generate short response (200 words)
            short_response = generate_email_response(
                email_text=customer_email,
                tone=tone,
                max_length=50,
                include_signature=include_signature,
                include_contact=include_contact,
                include_links=include_links,
                manager_note=manager_note,
                structured_emails=structured_emails
            )
            
            # Generate detailed response (500 words)
            detailed_response = generate_email_response(
                email_text=customer_email,
                tone=tone,
                max_length=100,
                include_signature=include_signature,
                include_contact=include_contact,
                include_links=include_links,
                manager_note=manager_note,
                structured_emails=structured_emails
            )
            
            st.success("Respostas geradas com sucesso!")
            
            # Display short response
            st.subheader("✉️ Resposta Curta (200 palavras):")
            st.text_area("", short_response, height=200)
            st.button("📋 Copiar Resposta Curta", 
                     on_click=lambda: st.write(short_response))
            
            # Display detailed response
            st.subheader("✉️ Resposta Detalhada (500 palavras):")
            st.text_area("", detailed_response, height=300)
            st.button("📋 Copiar Resposta Detalhada", 
                     on_click=lambda: st.write(detailed_response))
    else:
        st.warning("⚠️ Por favor insira o email do cliente")

# Add helpful footer
st.markdown("---")
st.markdown("© William Milner")
st.markdown("Desbloqueia novos horizontes com IA")
st.markdown("2025")