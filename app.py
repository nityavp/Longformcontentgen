import streamlit as st
import pandas as pd
import random
import zipfile
import os
import requests
from openai import OpenAI

# Text input for API key
api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Blog styles
blog_styles = [
    "The Ultimate Guide to [Keyword]",
    "Top 10 [Keyword] Tips for [Year]",
    "How to [Keyword] for Beginners",
    "What is [Keyword] and How Does It Work?",
    "Why is [Keyword] Important for [Industry/Activity]?",
    "How Can You Improve Your [Keyword]?",
    "10 Best [Keyword] Strategies",
    "7 Ways to Boost Your [Keyword]",
    "5 Common [Keyword] Mistakes to Avoid",
    "How to [Keyword] in [Number] Easy Steps",
    "A Step-by-Step Guide to [Keyword]",
    "How to Master [Keyword] Quickly",
    "The Benefits of [Keyword] for Your [Business/Life]",
    "Why [Keyword] is a Game-Changer for [Activity]",
    "How [Keyword] Can Improve Your [Specific Outcome]",
    "[Keyword] vs [Keyword]: Which is Better?",
    "Comparing [Keyword] and [Keyword]: Pros and Cons",
    "The Difference Between [Keyword] and [Keyword]",
    "How to Solve [Keyword] Problems",
    "Overcoming [Keyword] Challenges",
    "Solutions for [Keyword]: What You Need to Know",
    "How We Achieved [Result] with [Keyword]",
    "[Company/Person] Success Story: [Keyword] in Action",
    "The Impact of [Keyword] on [Specific Situation]",
    "The Latest Trends in [Keyword]",
    "What’s New in [Keyword] for [Year]?",
    "Future Predictions for [Keyword]",
    "[Keyword] Tips for [Specific Audience]",
    "What Every [Audience] Should Know About [Keyword]",
    "[Keyword] Strategies for [Audience]",
    "How to Prepare Your [Keyword] Strategy for [Season/Event]",
    "The Best [Keyword] Practices for [Holiday/Season]",
    "Maximizing [Keyword] During [Event]",
    "Effective [Keyword] Techniques You Can Use Today",
    "Quick Tips to Enhance Your [Keyword]",
    "Simple [Keyword] Hacks for Instant Results",
    "The Best Tools for [Keyword]",
    "Top Resources for Learning [Keyword]",
    "Free [Keyword] Resources You Need to Know About",
    "The Surprising Truth About [Keyword]",
    "Why You’re Struggling with [Keyword] (And How to Fix It)",
    "The Secret to [Keyword] Success",
    "Is [Keyword] Really Worth It?",
    "Why [Keyword] Might Be Overrated",
    "The Ugly Truth About [Keyword]"
]

# Initialize session state for posts data
if 'posts_data' not in st.session_state:
    st.session_state['posts_data'] = pd.DataFrame(columns=['Date', 'Content', 'Topic', 'Status'])

# Function to generate posts using the OpenAI API
def generate_posts(api_key, keyword, num_posts, custom_topic=None, additional_context=None):
    posts = []
    topics = []
    for _ in range(num_posts):
        if custom_topic:
            chosen_topic = custom_topic
        else:
            chosen_style = random.choice(blog_styles)
            chosen_topic = chosen_style.replace('[Keyword]', keyword)
        
        topics.append(chosen_topic)
        
        if additional_context:
            custom_prompt = f"Write an SEO friendly blog on the topic: '{chosen_topic}' with additional context: '{additional_context}'"
        else:
            custom_prompt = f"Write an SEO friendly blog on the topic: '{chosen_topic}'"
        
        messages = [{"role": "system", "content": custom_prompt}]
        try:
            client = OpenAI(api_key=api_key)
            completions = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            response = completions.choices[0].message.content
            posts.append(response)
        except Exception as e:
            st.error(f"Failed to generate posts: {e}")
            return [], []
    return posts, topics

# User interface for entering keyword and number of posts
keyword = st.text_input('Enter Keyword')
have_blog_idea = st.radio('Do you have a blog idea?', ['No', 'Yes'])

if have_blog_idea == 'Yes':
    custom_topic = st.text_input('Enter your blog topic')
    additional_context = None
    if st.radio('Do you have any additional context?', ['No', 'Yes']) == 'Yes':
        additional_context = st.text_area('Enter additional context')
else:
    custom_topic = None
    additional_context = None

num_posts = st.number_input('Number of Posts', min_value=1, max_value=20, value=1)
generate_btn = st.button('Generate Posts')

# Generate posts when button is clicked
if generate_btn:
    generated_posts, selected_topics = generate_posts(api_key, keyword, num_posts, custom_topic, additional_context)
    new_rows = [{'Date': pd.Timestamp('now'), 'Content': post, 'Topic': topic, 'Status': 'Pending'} for post, topic in zip(generated_posts, selected_topics)]
    st.session_state.posts_data = pd.concat([st.session_state.posts_data, pd.DataFrame(new_rows)], ignore_index=True)

# Display and edit the DataFrame containing generated posts
edited_data = st.experimental_data_editor(st.session_state.posts_data, num_rows='dynamic', use_container_width=True)

# Update session state with edited data
st.session_state.posts_data = edited_data

# Display the generated content
st.write("Generated Content")
for index, row in edited_data.iterrows():
    st.write(f"**Topic:** {row['Topic']}")
    st.write(f"**Content:** {row['Content']}")
    st.write("---")

# Function to create a zip file with content
def create_zip(content):
    zip_path = '/mnt/data/final_posts.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Save the content
        content_path = '/mnt/data/content.txt'
        with open(content_path, 'w') as f:
            f.write(content)
        zipf.write(content_path, 'content.txt')
        os.remove(content_path)
    
    return zip_path

# Allow user to select a row for downloading
selected_row = st.selectbox('Select a row to download content', edited_data.index)
if st.button('Download Selected Content'):
    selected_content = edited_data.loc[selected_row, 'Content']
    zip_path = create_zip(selected_content)
    with open(zip_path, "rb") as file:
        st.download_button('Download Content in Zip', file, file_name='final_posts.zip')


