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
def generate_posts(api_key, keyword, num_posts):
    posts = []
    topics = []
    for _ in range(num_posts):
        chosen_style = random.choice(blog_styles)
        topics.append(chosen_style.replace('[Keyword]', keyword))
        custom_prompt = f"Write an SEO friendly blog on the topic: '{chosen_style.replace('[Keyword]', keyword)}'"
        
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
num_posts = st.number_input('Number of Posts', min_value=1, max_value=20, value=1)
generate_btn = st.button('Generate Posts')

# Generate posts when button is clicked
if generate_btn:
    generated_posts, selected_topics = generate_posts(api_key, keyword, num_posts)
    new_rows = [{'Date': pd.Timestamp('now'), 'Content': post, 'Topic': topic, 'Status': 'Pending'} for post, topic in zip(generated_posts, selected_topics)]
    st.session_state.posts_data = pd.concat([st.session_state.posts_data, pd.DataFrame(new_rows)], ignore_index=True)

# Display and edit the DataFrame containing generated posts
edited_data = st.experimental_data_editor(st.session_state.posts_data, num_rows='dynamic', use_container_width=True)

# Update session state with edited data
st.session_state.posts_data = edited_data

# Function to generate an image based on selected row
def generate_image(api_key, style, content):
    try:
        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"{style} {content}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Failed to generate image: {e}")
        return None

# Function to create a zip file with content and image
def create_zip(content, image_url):
    zip_path = '/mnt/data/final_posts.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Save the content
        content_path = '/mnt/data/content.txt'
        with open(content_path, 'w') as f:
            f.write(content)
        zipf.write(content_path, 'content.txt')
        os.remove(content_path)
        
        # Download and save the image
        image_path = '/mnt/data/image.png'
        img_data = requests.get(image_url).content
        with open(image_path, 'wb') as f:
            f.write(img_data)
        zipf.write(image_path, 'image.png')
        os.remove(image_path)
    
    return zip_path

# Allow user to select a row
selected_row = st.selectbox('Select a row to generate an image', edited_data.index)
selected_style = st.text_input('Enter Image Style for Selected Row')
if st.button('Generate Image for Selected Row'):
    selected_content = edited_data.loc[selected_row, 'Content']
    image_url = generate_image(api_key, selected_style, selected_content)
    if image_url:
        st.image(image_url, caption='Generated Image')
        zip_path = create_zip(selected_content, image_url)
        with open(zip_path, "rb") as file:
            st.download_button('Download Content and Image in Zip', file, file_name='final_posts.zip')

