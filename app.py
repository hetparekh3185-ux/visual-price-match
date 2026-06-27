import os
import streamlit as st
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def upload_image_to_catbox(image_bytes, filename="upload.jpg"):
    """Uploads raw image bytes to Catbox.moe (no account/API key needed) and returns a public URL."""
    url = "https://catbox.moe/user/api.php"
    files = {"fileToUpload": (filename, image_bytes)}
    data = {"reqtype": "fileupload"}
    response = requests.post(url, data=data, files=files)

    if response.status_code == 200 and response.text.strip().startswith("https://"):
        return response.text.strip()
    else:
        print("CATBOX UPLOAD FAILED")
        print("Status code:", response.status_code)
        print("Response body:", response.text)
        st.error(f"Failed to upload image to cloud storage hosting. (Status: {response.status_code})")
        return None


def fetch_ecommerce_prices(public_image_url):
    """Sends the public image URL to Google Lens and returns parsed product listings."""
    params = {
        "engine": "google_lens",
        "url": public_image_url,
        "type": "visual_matches",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract visual shopping matches from the Lens payload
    visual_matches = results.get("visual_matches", [])
    products = []

    for item in visual_matches:
        title = item.get("title")
        link = item.get("link")
        price_obj = item.get("price")  # SerpApi returns this as an object: {"value": "$29.99", "extracted_value": 29.99, "currency": "$"}
        source = item.get("source")    # e.g., "Amazon", "eBay"
        thumbnail = item.get("thumbnail")

        if price_obj and price_obj.get("extracted_value") is not None:
            products.append({
                "title": title,
                "source": source,
                "link": link,
                "price_str": price_obj.get("value"),
                "price_val": price_obj.get("extracted_value"),
                "thumbnail": thumbnail
            })

    # Sort products mathematically from lowest price to highest price
    return sorted(products, key=lambda x: x["price_val"])


# --- Streamlit Frontend UI Configuration ---
st.set_page_config(page_title="Visual Price Matcher", layout="wide")
st.title(" Visual E-Commerce Price Matcher")
st.write("Upload an image of any product to scan the web and find the best live deals online.")

uploaded_file = st.file_uploader("Choose a product image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the user's uploaded image on screen
    st.image(uploaded_file, caption="Uploaded Product Preview", width=300)

    if st.button("Find Best Prices !"):
        with st.spinner("Processing image and crawling e-commerce sites..."):
            # Step 1: Read file as bytes
            img_bytes = uploaded_file.getvalue()

            # Step 2: Convert to public cloud link
            public_url = upload_image_to_catbox(img_bytes, uploaded_file.name)

            if public_url:
                # Step 3: Run the Reverse Visual Search Engine
                deals = fetch_ecommerce_prices(public_url)

                # Step 4: Display sorted results
                if deals:
                    st.success(f"Found {len(deals)} online store matches! Showing lowest prices first:")
                    for deal in deals:
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if deal["thumbnail"]:
                                st.image(deal["thumbnail"], width=100)
                        with col2:
                            st.subheader(f"{deal['price_str']} — {deal['source']}")
                            st.write(deal["title"])
                            st.markdown(f"[Go to Store Link]({deal['link']})")
                        st.markdown("---")
                else:
                    st.warning("No retail matches found with clear pricing data. Try a clearer product image.")
