import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
import time
from functools import lru_cache
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import html
import os
from dotenv import load_dotenv
import gdown

def download_models():
    files_to_download = {
        'movie_dict.pkl': '11RvGNvRH-2smDTLrdJ2ZcOLPHquvRTRq',
        'similarity_movies.pkl': '1IoPdFVTqj5NwBpW1jQyArQ670UjU1Lss',
        'similarity_songs.pkl': '1gjHEUt7hl4VNN4gzQKGzX2-LQtf52PT4',
        'popular.pkl': '1uLOJUn5sD1-Bnm_vDsONESsvImzBCAsG',
        'pt.pkl': '1bUSMUwKhHZS4CN9KTX-XbFq8iT9TPvQs',
        'books.pkl': '1kNQJKArgKIpz7NmznYARuqSG-N0PR3jp',
        'similarity_scores.pkl': '1W6FN-BIDd7kSSqLWaZOHgfMnUobBtqMv',
        'df.pkl': '18Wv2fsQIAZjaYtoOJVS5WgpbccoVifVS',
        'anime.pkl': '1MURQo1nQurTAMCPmPURluK6NbDvdnWJR',
        'similarity_anime.pkl': '1GsrqNetSz8sW2G-NK01jiXDIkWgmptcc',
        'anime_indices.pkl': '1Dwj3Vlsx-FuB5ghChtycaCH16T2nEYvA',
        'rating.csv': '1r5efPywImnecYDQaA0hnygqc_ID6BpDW', 
        'games.pkl': '1XiOSLzOx3HDcT8kwZZqgeh02DowbLbYG',
        'cosine_sim.pkl': '1305Z_qsv8rjdb_7MxH9rh-4AkizQOycq'
    }
    failed_files = []
    for filename, file_id in files_to_download.items():
        if not os.path.exists(filename):
            print(f"File {filename} missing. Downloading...")
            url = f'https://drive.google.com/uc?id={file_id}'
            try:
                gdown.download(url, filename, quiet=False, fuzzy=True)
                print(f"✓ Successfully downloaded {filename}")
            except Exception as e:
                print(f"✗ Failed to download {filename}: {str(e)}")
                failed_files.append(filename)
        else:
            print(f"File {filename} already exists, skipping.")
    
    if failed_files:
        print(f"\n⚠️  Warning: Failed to download {len(failed_files)} file(s): {', '.join(failed_files)}")
        print("The app will continue, but some features may not work.")

download_models()

# Load environment variables
load_dotenv()

# Get API keys from environment variables or Streamlit secrets
try:
    SPOTIFY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID", os.getenv('SPOTIFY_CLIENT_ID', '5d63c8dd552d458d84c1db09fb2aa897'))
    SPOTIFY_CLIENT_SECRET = st.secrets.get("SPOTIFY_CLIENT_SECRET", os.getenv('SPOTIFY_CLIENT_SECRET', '55422e4759a541a2ad3625e83a88bd8e'))
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", os.getenv('TMDB_API_KEY', '84f51736bbe0caea6e528d85d1a56234'))
except:
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '5d63c8dd552d458d84c1db09fb2aa897')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '55422e4759a541a2ad3625e83a88bd8e')
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '84f51736bbe0caea6e528d85d1a56234')

# ============================ Page Config and CSS ============================

st.set_page_config(
    page_title="Entertainment Universe",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [All your CSS - keeping it exactly as is]
st.markdown("""
<style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.5),
                        0 0 20px rgba(102, 126, 234, 0.3),
                        0 0 30px rgba(102, 126, 234, 0.2);
        }
        50% {
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.8),
                        0 0 40px rgba(102, 126, 234, 0.5),
                        0 0 60px rgba(102, 126, 234, 0.3);
        }
    }
    
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #0f0c29);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    .header-image-container-top {
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        animation: fadeInMoveDown 2s ease forwards;
        position: relative;
    }
    
    .header-image-container-top::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes fadeInMoveDown {
        0% {
            opacity: 0;
            transform: translateY(-50px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .header-image-container {
        width: 100%;
        max-height: 400px;
        object-fit: cover;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8);
        animation: fadeInUp 1s ease;
    }
    
    .header-image-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.3) 100%);
        pointer-events: none;
    }
    
    .header-image-container img {
        width: 100%;
        max-height: 400px;
        object-fit: cover;
        border-radius: 20px;
        transition: transform 0.5s ease;
    }
    
    .header-image-container:hover img {
        transform: scale(1.05);
    }
    
    .nav-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: fadeInUp 0.8s ease;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes floatEmoji {
        0%, 100% { 
            transform: translateY(0px) rotate(0deg); 
        }
        25% { 
            transform: translateY(-10px) rotate(-5deg); 
        }
        50% { 
            transform: translateY(-15px) rotate(0deg); 
        }
        75% { 
            transform: translateY(-10px) rotate(5deg); 
        }
    }
    
    @keyframes textGlow {
        0%, 100% {
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.5),
                         0 0 20px rgba(102, 126, 234, 0.3),
                         0 0 30px rgba(118, 75, 162, 0.2);
        }
        50% {
            text-shadow: 0 0 20px rgba(102, 126, 234, 0.8),
                         0 0 40px rgba(102, 126, 234, 0.5),
                         0 0 60px rgba(118, 75, 162, 0.4);
        }
    }
    
    @keyframes slideInScale {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes decorativeLine {
        0% {
            width: 0%;
            opacity: 0;
        }
        50% {
            opacity: 1;
        }
        100% {
            width: 100%;
            opacity: 1;
        }
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 50px 30px;
        margin: 30px 0;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: slideInScale 1s ease;
        position: relative;
        overflow: hidden;
    }
    
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        animation: gradientShift 10s ease infinite;
    }
    
    .hero-main-title {
        font-size: 3.5rem !important;
        font-weight: 900;
        margin-bottom: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 5s ease infinite, textGlow 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
        letter-spacing: 2px;
    }
    
    .emoji-float {
        display: inline-block;
        animation: floatEmoji 3s ease-in-out infinite;
        font-size: 3.5rem;
        filter: drop-shadow(0 5px 15px rgba(102, 126, 234, 0.4));
    }
    
    .emoji-float:first-child {
        animation-delay: 0s;
    }
    
    .emoji-float:last-child {
        animation-delay: 1.5s;
    }
    
    .hero-subtitle-box {
        position: relative;
        z-index: 1;
        animation: fadeInUp 1.2s ease 0.3s both;
    }
    
    .hero-welcome {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 15px;
        animation: fadeInUp 1.4s ease 0.5s both;
        text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .hero-description {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1.3rem;
        line-height: 1.8;
        max-width: 900px;
        margin: 0 auto;
        animation: fadeInUp 1.6s ease 0.7s both;
    }
    
    .highlight-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        position: relative;
        display: inline-block;
        padding: 0 5px;
        transition: all 0.3s ease;
    }
    
    .highlight-text::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .highlight-text:hover::after {
        transform: scaleX(1);
    }
    
    .decorative-line {
        width: 0%;
        height: 4px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, #667eea, transparent);
        margin: 30px auto 0;
        border-radius: 2px;
        animation: decorativeLine 2s ease 1s forwards;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
    }
    
    h1 {
        animation: fadeInDown 1s ease-out;
        text-align: center;
        color: #ffffff;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        font-size: 3rem !important;
        padding: 20px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
    }
    
    h1::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 3px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
        animation: pulse 2s ease infinite;
    }
    
    .item-image {
        width: 100%;
        aspect-ratio: 2/3;
        object-fit: cover;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .item-image:hover {
        transform: scale(1.08) translateY(-10px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        animation: glow 2s ease infinite;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.8);
        transform: translateY(-3px);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .placeholder-image {
        width: 100%;
        aspect-ratio: 2/3;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 48px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        animation: pulse 3s ease infinite;
    }
    
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        padding: 40px;
        margin: 30px 0;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.1);
        animation: fadeInUp 1.2s ease;
    }
    
    .hero-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: float 3s ease-in-out infinite;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.2rem;
        margin-bottom: 30px;
        animation: fadeInUp 1.5s ease;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease;
        animation-fill-mode: both;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .feature-card:nth-child(1) { animation-delay: 0.1s; }
    .feature-card:nth-child(2) { animation-delay: 0.2s; }
    .feature-card:nth-child(3) { animation-delay: 0.3s; }
    .feature-card:nth-child(4) { animation-delay: 0.4s; }
    .feature-card:nth-child(5) { animation-delay: 0.5s; }
    
    .feature-icon {
        font-size: 48px;
        margin-bottom: 15px;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
    }
    
    .feature-title {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .feature-description {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
    }

    .book-row {
        display: flex;
        gap: 15px;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .book-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
        flex: 1 1 18%;
        min-width: 150px;
        max-width: 180px;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 370px;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease;
        animation-fill-mode: both;
    }
    
    .book-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s;
    }
    
    .book-card:hover::after {
        left: 100%;
    }
    
    .book-card:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.5);
    }
    
    .book-image {
        width: 100%;
        height: 270px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .book-card:hover .book-image {
        transform: scale(1.05);
    }
    
    .book-title {
        color: #fff;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        min-height: 48px;
        margin-bottom: 6px;
    }
    
    .book-author {
        color: #bbb;
        font-size: 14px;
        text-align: center;
        font-style: italic;
    }

    .footer {
        background: linear-gradient(135deg, rgba(20, 20, 40, 0.95) 0%, rgba(30, 30, 60, 0.95) 100%);
        backdrop-filter: blur(15px);
        border-top: 2px solid rgba(102, 126, 234, 0.3);
        color: white;
        text-align: center;
        padding: 30px 20px;
        margin-top: 50px;
        border-radius: 20px 20px 0 0;
        animation: fadeInUp 1s ease;
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 200%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        animation: shimmer 5s infinite;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }
    
    .footer-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: pulse 2s ease infinite;
    }
    
    .footer-icons {
        display: flex;
        justify-content: center;
        gap: 20px;
        font-size: 32px;
        margin: 20px 0;
        animation: float 3s ease-in-out infinite;
    }
    
    .footer-contact {
        display: flex;
        justify-content: center;
        gap: 30px;
        flex-wrap: wrap;
        margin-top: 20px;
    }
    
    .contact-item {
        background: rgba(102, 126, 234, 0.2);
        padding: 10px 20px;
        border-radius: 20px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .contact-item::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.4s, height 0.4s;
    }
    
    .contact-item:hover::before {
        width: 200px;
        height: 200px;
    }
    
    .contact-item:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
    }
    
    .footer-rights {
        margin-top: 20px;
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
    }
    
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 12, 41, 0.95) 0%, rgba(48, 43, 99, 0.95) 100%);
        backdrop-filter: blur(10px);
    }
    
    .stImage {
        animation: fadeInUp 0.6s ease;
        animation-fill-mode: both;
    }
    
    .stSpinner > div {
        border-color: #667eea transparent #764ba2 transparent !important;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .stSelectbox {
        animation: fadeInUp 0.8s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);    
    }
</style>
""", unsafe_allow_html=True)

# ============================ Session State ============================
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ============================ Sidebar Navigation ===============================
with st.sidebar:
    st.markdown("### 🎬 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
    if st.button("🎬 Movie Recommender", use_container_width=True):
        st.session_state.page = 'movies'
    if st.button("📚 Books Recommender", use_container_width=True):
        st.session_state.page = 'books'
    if st.button("🎵 Music Recommender", use_container_width=True):
        st.session_state.page = 'music'
    if st.button("🎌 Anime Recommender", use_container_width=True):
        st.session_state.page = 'anime'
    if st.button("🎮 Game Recommender", use_container_width=True):
        st.session_state.page = 'games'

from streamlit_autorefresh import st_autorefresh

def show_home():
    carousel_images = [
        ("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&h=400&fit=crop", "🎬 Movies"),
        ("https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=1200&h=400&fit=crop", "📚 Books"),
        ("https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=1200&h=400&fit=crop", "🎵 Music"),
        ("https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&h=400&fit=crop", "🎌 Anime"),
        ("https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=1200&h=400&fit=crop", "🎮 Games"),
    ]

    count = st_autorefresh(interval=10000, limit=None, key="autorefresh")
    carousel_index = count % len(carousel_images)
    current_img_url, current_caption = carousel_images[carousel_index]

    st.markdown(f"""
    <div class="header-image-container">
        <img src="{current_img_url}" alt="{current_caption}">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-main-title">
            <span class="emoji-float">🎬</span> 
            Entertainment Universe 
            <span class="emoji-float">🎮</span>
        </h1>
        <div class="hero-subtitle-box">
            <p class="hero-welcome">Welcome to Your Ultimate Entertainment Hub!</p>
            <p class="hero-description">
                Discover personalized recommendations across 
                <span class="highlight-text">movies</span>, 
                <span class="highlight-text">books</span>, 
                <span class="highlight-text">music</span>, 
                <span class="highlight-text">anime</span>, and 
                <span class="highlight-text">games</span>
            </p>
        </div>
        <div class="decorative-line"></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### ✨ What We Offer")
    cols = st.columns(3)
    features = [
        ("🎯", "Smart Recommendations", "AI-powered suggestions based on your preferences"),
        ("🌟", "Trending Content", "Discover what's popular right now"),
        ("🎨", "Beautiful Interface", "Enjoy a seamless and elegant experience"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        col.markdown(f"""
        <div class="feature-card">
            <div style="font-size:48px;">{icon}</div>
            <div style="color:white;font-size:1.5rem;font-weight:bold;">{title}</div>
            <div style="color:rgba(255,255,255,0.7);">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🎪 Browse by Category")
    cat_cols = st.columns(2)
    left_cats = [("🎬", "Movies", "Get personalized movie recommendations."),
                 ("🎵", "Music", "Discover new songs similar to your favorites."),
                 ("🎮", "Games", "Find free-to-play games you'll love.")]
    right_cats = [("📚", "Books", "Explore trending books and personalized reads."),
                  ("🎌", "Anime", "Find anime similar to your favorites.")]

    for icon, title, desc in left_cats:
        cat_cols[0].markdown(f"<div class='feature-card'><div style='font-size:48px;'>{icon}</div><div style='color:white;font-weight:bold;'>{title}</div><div style='color:#ccc;'>{desc}</div></div>", unsafe_allow_html=True)
    for icon, title, desc in right_cats:
        cat_cols[1].markdown(f"<div class='feature-card'><div style='font-size:48px;'>{icon}</div><div style='color:white;font-weight:bold;'>{title}</div><div style='color:#ccc;'>{desc}</div></div>", unsafe_allow_html=True)

@lru_cache(maxsize=5000)
def fetch_movie_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    except:
        return None

def recommend_movies(movie, movies, similarity):
    if movie not in movies['title'].values:
        return [], []
    movie_index = movies[movies['title']==movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        time.sleep(0.2)
        poster_url = fetch_movie_poster(movie_id)
        recommended_posters.append(poster_url)
    return recommended_movies, recommended_posters

@st.cache_resource
def load_movie_data():
    """Load movie data with caching"""
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity_movies.pkl', 'rb'))
    return movies, similarity

def show_movies():
    st.markdown('<h1>🎬 Movie Recommender</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="header-image-container">
        <img src="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&h=300&fit=crop" alt="Movies">
    </div>
    """, unsafe_allow_html=True)
    try:
        movies, similarity = load_movie_data()
        st.markdown("### Select a movie to get recommendations")
        selected_movie = st.selectbox("Choose a movie:", movies['title'].values, key='movie_select')
        if st.button('Get Recommendations', key='movie_btn'):
            with st.spinner('Finding similar movies...'):
                names, posters = recommend_movies(selected_movie, movies, similarity)
                if not names:
                    st.warning("Selected movie not found in the database.")
                    return
                cols = st.columns(5)
                for idx, col in enumerate(cols):
                    with col:
                        st.markdown(f'**{names[idx]}**')
                        if posters[idx]:
                            st.image(posters[idx], use_container_width=True)
                        else:
                            st.markdown('<div class="placeholder-image">🎬</div>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Movie data files not found. Please ensure 'movie_dict.pkl' and 'similarity_movies.pkl' are in the directory.")
    except Exception as e:
        st.error(f"Error: {e}")

def show_books():
    if "book_page" not in st.session_state:
        st.session_state.book_page = "popular"

    st.markdown("<h1 style='text-align:center;'>📚 Books Section</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔥 Top 50 Books", use_container_width=True):
            st.session_state.book_page = "popular"
    with c2:
        if st.button("🎯 Recommend Books", use_container_width=True):
            st.session_state.book_page = "recommend"
    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.book_page == "popular":
        try:
            popular_df = pickle.load(open("popular.pkl", "rb"))
            image_col = None
            for col_name in ["Image-URL-M", "Image_URL_M", "image_url_m"]:
                if col_name in popular_df.columns:
                    image_col = col_name
                    break

            if not image_col:
                st.error("Image URL column not found in the data.")
            else:
                filtered = popular_df.dropna(subset=[image_col, "Book-Title", "Book-Author"])
                filtered = filtered[filtered[image_col] != ""]
                filtered = filtered[filtered["Book-Title"] != ""]
                filtered = filtered[filtered["Book-Author"] != ""]

                top_books = filtered.head(50)
                
                st.markdown("### 🔥 Top 50 Popular Books")
                
                num_columns = 5
                for i in range(0, len(top_books), num_columns):
                    cols = st.columns(num_columns)
                    
                    for j in range(num_columns):
                        idx = i + j
                        if idx < len(top_books):
                            with cols[j]:
                                row = top_books.iloc[idx]
                                image_url = row[image_col]
                                title = row["Book-Title"]
                                author = row["Book-Author"]
                                
                                st.markdown(f"""
                                <div class="book-card">
                                    <img src="{image_url}" class="book-image" alt="{title}">
                                    <div class="book-title">{html.escape(title)}</div>
                                    <div class="book-author">{html.escape(author)}</div>
                                </div>
                                """, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error("Book data 'popular.pkl' not found!")
        except Exception as e:
            st.error(f"Error loading book data: {e}")

    elif st.session_state.book_page == "recommend":
        try:
            pt = pickle.load(open("pt.pkl", "rb"))
            books = pickle.load(open("books.pkl", "rb"))
            similarity_scores = pickle.load(open("similarity_scores.pkl", "rb"))
            book_titles = pt.index.tolist()

            selected_book = st.selectbox("Select a book:", book_titles)
            if st.button("Get Recommendations", use_container_width=True):
                index = np.where(pt.index == selected_book)[0][0]
                similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]
                data = []
                for i in similar_items:
                    temp_df = books[books["Book-Title"] == pt.index[i[0]]]
                    if temp_df.empty:
                        continue
                    book_title = temp_df["Book-Title"].values[0]
                    book_author = temp_df["Book-Author"].values[0]
                    image_url = None
                    for col_name in ["Image-URL-M", "Image_URL_M", "image_url_m"]:
                        if col_name in temp_df.columns:
                            image_url = temp_df[col_name].values[0]
                            break
                    if not image_url or pd.isna(image_url) or image_url == "":
                        image_url = "https://via.placeholder.com/150x270.png?text=No+Image"

                    data.append([book_title, book_author, image_url])

                st.markdown("### 📚 Recommended Books")
                cols = st.columns(5)
                for idx, book in enumerate(data):
                    col = cols[idx % 5]
                    with col:
                        st.markdown(f"""
                        <div class="book-card">
                            <img src="{book[2]}" class="book-image" alt="{book[0]}">
                            <div class="book-title">{html.escape(book[0])}</div>
                            <div class="book-author">{html.escape(book[1])}</div>
                        </div>
                        """, unsafe_allow_html=True)

        except FileNotFoundError:
            st.error("Required files 'pt.pkl', 'books.pkl', or 'similarity_scores.pkl' are missing.")
        except Exception as e:
            st.error(f"Error during recommendation: {e}")

def get_song_album_cover(song_name, artist_name):
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID, 
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        search_query = f"track:{song_name} artist:{artist_name}"
        results = sp.search(q=search_query, type="track")
        if results and results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            return track["album"]["images"][0]["url"]
        return "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400&h=600&fit=crop"
    except:
        return "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400&h=600&fit=crop"

def recommend_music(song, music, similarity):
    if song not in music['song'].values:
        return [], []
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_names = []
    recommended_posters = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        recommended_posters.append(get_song_album_cover(music.iloc[i[0]].song, artist))
        recommended_names.append(music.iloc[i[0]].song)
    return recommended_names, recommended_posters

@st.cache_resource
def load_music_data():
    """Load music data with caching to prevent memory issues"""
    try:
        music = pickle.load(open('df.pkl', 'rb'))
        similarity = pickle.load(open('similarity_songs.pkl', 'rb'))
        return music, similarity
    except Exception as e:
        st.error(f"Error loading music data: {e}")
        return None, None

def show_music():
    st.markdown('<h1>🎵 Music Recommender</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="header-image-container">
        <img src="https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=1200&h=300&fit=crop" alt="Music">
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Load data with caching
        with st.spinner('Loading music database...'):
            music, similarity = load_music_data()
        
        if music is None or similarity is None:
            st.error("Failed to load music data. Please try refreshing the page.")
            return
        
        st.markdown("### Select a song to get recommendations")
        music_list = music['song'].values
        selected_song = st.selectbox("Choose a song:", music_list, key='music_select')
        
        if st.button('Get Recommendations', key='music_btn'):
            with st.spinner('Finding similar songs...'):
                try:
                    names, posters = recommend_music(selected_song, music, similarity)
                    if not names:
                        st.warning("Selected song not found in the database.")
                        return
                    cols = st.columns(5)
                    for idx, col in enumerate(cols):
                        with col:
                            st.markdown(f'**{names[idx]}**')
                            st.image(posters[idx], use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
                    st.info("Try selecting a different song or refresh the page.")
                    
    except FileNotFoundError:
        st.error("Music data files not found. Please ensure 'df.pkl' and 'similarity_songs.pkl' are in the directory.")
    except MemoryError:
        st.error("⚠️ Memory limit exceeded. The music recommendation feature requires significant memory. Please try again later or contact support.")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        st.info("Please refresh the page and try again.")

def fetch_anime_poster(anime_name):
    try:
        url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
        response = requests.get(url, timeout=10).json()
        if 'data' in response and len(response['data']) > 0:
            return response['data'][0]['images']['jpg']['large_image_url']
        else:
            return "https://i.postimg.cc/8cNyqB2v/anime-placeholder.jpg"
    except:
        return "https://i.postimg.cc/8cNyqB2v/anime-placeholder.jpg"

def recommend_anime(title, anime, cosine_sim, anime_indices, top_n=10):
    idx = anime_indices.get(title)
    if idx is None:
        return [], []
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    anime_indices_top = [i[0] for i in sim_scores]
    recommended_names = anime['name'].iloc[anime_indices_top].tolist()
    recommended_posters = [fetch_anime_poster(name) for name in recommended_names]
    return recommended_names, recommended_posters

def get_popular_anime(anime):
    rating_anime = pd.read_csv('rating.csv')
    ratings_cleaned = rating_anime[rating_anime['rating'] != -1]
    anime_rating_count = ratings_cleaned.groupby('anime_id')['rating'].count().reset_index()
    anime_rating_count.columns = ['anime_id', 'num_ratings']
    popularity_df = anime_rating_count.merge(anime[['anime_id', 'name']], on='anime_id')
    top_popular = popularity_df.sort_values(by='num_ratings', ascending=False).head(50)
    return top_popular

def show_anime():
    st.markdown('<h1>🎌 Anime Recommender</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="header-image-container">
        <img src="https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&h=300&fit=crop" alt="Anime">
    </div>
    """, unsafe_allow_html=True)
    
    try:
        anime = pickle.load(open('anime.pkl', 'rb'))
        cosine_sim = pickle.load(open('similarity_anime.pkl', 'rb'))
        anime_indices = pickle.load(open('anime_indices.pkl', 'rb'))
        
        st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔥 Popular", key="popular_btn", use_container_width=True):
                st.session_state.anime_page = "popular"
        with col2:
            if st.button("🎯 Recommend", key="recommend_btn", use_container_width=True):
                st.session_state.anime_page = "recommend"
        st.markdown("</div>", unsafe_allow_html=True)

        if "anime_page" not in st.session_state:
            st.session_state.anime_page = "popular"

        if st.session_state.anime_page == "popular":
            st.header("🔥 Top 50 Most Popular Anime")
            top_popular = get_popular_anime(anime)
            
            for i in range(0, len(top_popular), 5):
                cols = st.columns(5)
                for j in range(5):
                    idx = i + j
                    if idx < len(top_popular):
                        with cols[j]:
                            row = top_popular.iloc[idx]
                            poster_url = fetch_anime_poster(row['name'])
                            
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <img src="{poster_url}" style="width: 100%; height: 300px; object-fit: cover; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                                <div style="color: white; margin-top: 10px; font-weight: bold; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 14px;">
                                    {html.escape(row['name'])}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

        elif st.session_state.anime_page == "recommend":
            st.header("🎯 Find Similar Anime by Genre")
            selected_anime = st.selectbox("Select an anime:", anime['name'].values)
            if st.button("Show Recommendations", key="show_btn"):
                names, posters = recommend_anime(selected_anime, anime, cosine_sim, anime_indices)
                if names:
                    for i in range(0, len(names), 5):
                        cols = st.columns(5)
                        for j in range(5):
                            idx = i + j
                            if idx < len(names):
                                with cols[j]:
                                    poster_url = posters[idx]
                                    anime_name = names[idx]
                                    
                                    st.markdown(f"""
                                    <div style="text-align: center;">
                                        <img src="{poster_url}" style="width: 100%; height: 300px; object-fit: cover; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                                        <div style="color: white; margin-top: 10px; font-weight: bold; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 14px;">
                                            {html.escape(anime_name)}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.warning("No similar anime found.")
    except FileNotFoundError:
        st.error("Anime data files not found.")
    except Exception as e:
        st.error(f"Error: {e}")

def get_top_50_games(df):
    df_sorted = df.sort_values(by='release_date', ascending=False)
    return df_sorted[['title', 'thumbnail', 'genre', 'publisher', 'release_date']].head(50)

def recommend_games(title, df, cosine_sim, top_n=5):
    if title not in df['title'].values:
        return [], []
    idx = df.index[df['title'] == title][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    game_idxs = [i[0] for i in sim_scores]
    names = df['title'].iloc[game_idxs].tolist()
    thumbs = df['thumbnail'].iloc[game_idxs].tolist()
    return names, thumbs

def show_games():
    st.markdown('<h1>🎮 Game Recommender</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="header-image-container">
        <img src="https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=1200&h=300&fit=crop" alt="Games">
    </div>
    """, unsafe_allow_html=True)

    try:
        df = pickle.load(open('games.pkl', 'rb'))
        cosine_sim = pickle.load(open('cosine_sim.pkl', 'rb'))
        
        tab1, tab2 = st.tabs(["🔥 Top 50 Games", "🎯 Recommend Games"])
        
        with tab1:
            st.header("🔥 Top 50 Recent Free-to-Play Games")
            top50 = get_top_50_games(df)
            cols_per_row = 5
            rows = (len(top50) + cols_per_row - 1) // cols_per_row
            for r in range(rows):
                cols = st.columns(cols_per_row)
                for c in range(cols_per_row):
                    idx = r * cols_per_row + c
                    if idx < len(top50):
                        game = top50.iloc[idx]
                        with cols[c]:
                            st.image(game['thumbnail'], use_container_width=True)
                            st.caption(f"**{game['title']}**\n\nGenre: {game['genre']}\nPublisher: {game['publisher']}\nRelease: {game['release_date']}")

        with tab2:
            st.header("🎯 Get Game Recommendations")
            selected_game = st.selectbox("Select a game:", df['title'].values, key='game_select')
            if st.button('Get Recommendations', key='game_btn'):
                with st.spinner('Finding similar games...'):
                    names, thumbs = recommend_games(selected_game, df, cosine_sim)
                    if names:
                        cols = st.columns(5)
                        for idx, col in enumerate(cols):
                            with col:
                                st.markdown(f'**{names[idx]}**')
                                st.image(thumbs[idx], use_container_width=True)
                    else:
                        st.warning("No similar games found.")

    except FileNotFoundError:
        st.error("Game data files not found.")
    except Exception as e:
        st.error(f"Error: {e}")

# ============================ Main App Routing ================================

if st.session_state.page == 'home':
    show_home()
elif st.session_state.page == 'movies':
    show_movies()
elif st.session_state.page == 'books':
    show_books()
elif st.session_state.page == 'music':
    show_music()
elif st.session_state.page == 'anime':
    show_anime()
elif st.session_state.page == 'games':
    show_games()

# ============================ Footer ========================================

st.markdown("""
<div class="footer">
    <div class="footer-content">
        <div class="footer-title">🎬 Entertainment Universe 🎮</div>
        <div class="footer-icons">
            🎬 📚 🎵 🎌 🎮
        </div>
        <div style="margin: 15px 0;">
            <span style="font-size: 18px;">Made with ❤️ by <strong>Ayush</strong></span>
        </div>
        <div class="footer-contact">
            <div class="contact-item">📞 9835237626</div>
            <div class="contact-item">📧 ayushashish1111@gmail.com</div>
        </div>
        <div class="footer-rights">
            © 2025 Entertainment Universe. All Rights Reserved.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)