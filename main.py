import streamlit as st
import json
from openai import OpenAI
api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="AI Product Review Analyzer", layout="wide")
st.title("📦 ReviewSense")

uploaded_file = st.file_uploader("📤 Upload your reviews JSON", type="json")

def display_stars(rating):
    return "⭐" * rating + "☆" * (5 - rating)

if uploaded_file:
    product_reviews = json.load(uploaded_file)

    # Show button above reviews
    if st.button("✨ Generate AI Summary"):
        with st.spinner("🔍 Step 1: Extracting pros and cons..."):
            extract_prompt = f"""
You are a professional customer review analyst.

Your task is to extract **key pros and cons** from each review. Provide the output as a **list of dictionaries**, where each dictionary represents a review and contains:
- "pros": A list of specific positive points
- "cons": A list of specific negative points

Only include factual or sentiment-backed observations (not vague statements).

Example format:
[
  {{
    "pros": ["Excellent display in sunlight", "Fast performance"],
    "cons": ["Battery drains fast"]
  }},
  ...
]

Here are the reviews:
{json.dumps(product_reviews, indent=2)}
"""
            extract_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant trained to analyze product reviews."},
                    {"role": "user", "content": extract_prompt}
                ]
            )
            pros_cons_output = extract_response.choices[0].message.content.strip()
            st.success("✅ Step 1: Extracted Pros and Cons")
            st.code(pros_cons_output, language="json")

        with st.spinner("📊 Step 2: Grouping similar themes..."):
            group_prompt = f"""
You are an AI assistant helping to synthesize customer feedback.

From the extracted pros and cons below, identify **common themes** by grouping similar or semantically equivalent feedback into categories.

Return a JSON object with:
- "common_pros": List of grouped positive themes
- "common_cons": List of grouped negative themes

Avoid repeating similar items.

Example output:
{{
  "common_pros": ["Excellent camera performance", "Bright and vibrant display", "Fast and smooth app experience"],
  "common_cons": ["Battery drains quickly", "Device gets warm during usage"]
}}

Extracted pros and cons:
{pros_cons_output}
"""
            group_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": group_prompt}]
            )
            grouped_feedback = group_response.choices[0].message.content.strip()
            st.success("✅ Step 2: Grouped Feedback")
            st.code(grouped_feedback, language="json")

        with st.spinner("🧾 Step 3: Writing summary report..."):
            summary_prompt = f"""
You are an AI product analyst.

Using the grouped customer feedback below, write a professional summary highlighting the main strengths and weaknesses of the product.

Structure:
**Strengths**
- Bullet point 1
- Bullet point 2
- ...

**Weaknesses**
- Bullet point 1
- Bullet point 2
- ...

Limit each section to **3–4 concise points**. Make it useful for product managers and stakeholders.

Grouped Feedback:
{grouped_feedback}
"""
            summary_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary_report = summary_response.choices[0].message.content.strip()
            st.success("✅ Step 3: Summary Ready")
            st.markdown("### 📋 AI-Generated Product Summary")
            st.markdown(summary_report)

    # Display all customer reviews below
    st.markdown("### 📝 Customer Reviews")
    for review in product_reviews:
        st.markdown("---")
        st.markdown(f"**{review['name']}**")
        st.markdown(f"{display_stars(review['rating'])} &nbsp;&nbsp; **{review['title']}**", unsafe_allow_html=True)
        st.markdown(f" {review['date']}")
        st.markdown(
                f"<span style='color:gray'>Colour:</span> {review['color']} &nbsp; | &nbsp; "
                f"<span style='color:gray'>Size:</span> {review['size']} &nbsp; | &nbsp; "
                f"{'✅ <span style=\"color:orange\">Verified Purchase</span>' if review.get('verified') else ''}",
                unsafe_allow_html=True
            )
        st.markdown(review["review"])
