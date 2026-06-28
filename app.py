import os
import base64
import streamlit as st
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load credentials — works both locally (.env) and on Streamlit Cloud (st.secrets)
load_dotenv()
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY") or os.getenv("SERPAPI_KEY")
IMGBB_API_KEY = st.secrets.get("IMGBB_API_KEY") or os.getenv("IMGBB_API_KEY")


def upload_image_to_imgbb(image_bytes, filename="upload.jpg"):
    """Uploads raw image bytes to ImgBB and returns a public URL."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API_KEY,
            "image": b64,
            "name": filename
        }
    )
    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        print("IMGBB UPLOAD FAILED")
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

    visual_matches = results.get("visual_matches", [])
    products = []

    for item in visual_matches:
        title = item.get("title")
        link = item.get("link")
        price_obj = item.get("price")
        source = item.get("source")
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

    return sorted(products, key=lambda x: x["price_val"])


# --- Streamlit Frontend UI Configuration ---
st.set_page_config(page_title="Visual Price Matcher", layout="wide")
st.title("Visual E-Commerce Price Matcher")
st.write("Upload an image of any product to scan the web and find the best live deals online.")

uploaded_file = st.file_uploader("Choose a product image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Product Preview", width=300)

    if st.button("Find Best Prices !"):
        with st.spinner("Processing image and crawling e-commerce sites..."):
            img_bytes = uploaded_file.getvalue()
            public_url = upload_image_to_imgbb(img_bytes, uploaded_file.name)

            if public_url:
                deals = fetch_ecommerce_prices(public_url)

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
