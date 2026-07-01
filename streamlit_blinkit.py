import csv
import hashlib
import pickle
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "white.py.csv"
PICKLE_PATH = BASE_DIR / "blinkit_pickle"

with PICKLE_PATH.open("rb") as f:
    model = pickle.load(f)

st.set_page_config(layout="wide")
st.title("🧃 THE FLAVOR FACTORY 🧃")
st.markdown("""
<style>
[data-testid="stImage"] img {
    max-height: 320px;
    object-fit: contain;
    width: 100%;
}
[data-testid="stImage"] {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 320px;
}
</style>
""", unsafe_allow_html=True)

DEFAULT_IMAGE = str((BASE_DIR / 'product_placeholder.svg').resolve())
IMAGE_CACHE_DIR = BASE_DIR / 'image_cache'
IMAGE_CACHE_DIR.mkdir(exist_ok=True)
BRAND_IMAGE_URLS = {
    'kingfisher': 'https://api.mircate.com/5p1hp1d2t/CALL/PIMAPI/getImage/jux9er4tf08?filename=jux9er4tf08-7cf533a774aa43d49ee0766c0617d901.png&quality=100',
    'tuborg': 'http://kaltoggott.is/cdn/shop/files/Classic500.jpg?v=1758314587',
    'budweiser': 'https://www.cantechonline.com/wp-content/uploads/Budweiser-alu-beer-bottle_2014-Fifa-World-cup.jpg',
    'corona': 'https://licoresmaduro.com/wp-content/uploads/2023/10/4860.png',
    'old monk': 'https://antiquitywhisky.in/wp-content/uploads/2024/08/Old-Monk-rum-price-in-India-Latest-August-Updated-Price-1.webp',
    'bacardi': 'https://alto1994.com/tienda/27924-large_default/ron-bacardi-big-apple-1l-35-12.jpg',
    'captain morgan': 'https://images.squarespace-cdn.com/content/v1/5eb05eb2b88ab04655228885/1655630271571-AWDLF2YWZLB82IKFR33O/Captain-Morgan-Tiki-Mango-Pineapple-Rum-The-Rum-Company.jpg',
    'royal stag': 'https://olkeriliquor.com/wp-content/uploads/2023/06/ROYAL-STAG-750ML-WHISKY.jpg',
    'blenders pride': 'https://curlytales.com/wp-content/uploads/2023/09/Blenders-Pride.jpg',
    'jack daniels': 'https://halftimebeverage.com/media/catalog/product/cache/5a9ece781d558937ae51db0fc99c94f4/rdi/rdi/jack-daniels-cherry-lime-46-20485_1.png',
    'coca-cola': 'https://www.awesomeinventions.com/wp-content/uploads/2019/11/Coca-Cola-Cinnamon-and-Sprite-Winter-Spiced-Cranberry.jpg',
    'pepsi': 'https://products.pepsico.ua/uploads/products/Pepsi_Pineapple_Peach_Beverages_1000.jpg',
    'sprite': 'https://5.imimg.com/data5/SELLER/Default/2023/3/296218244/ZM/YN/HI/130701409/250ml-sprite-cold-drink-1000x1000.jpg',
    'fanta': 'http://popsnaxworld.com/cdn/shop/files/BlueberryFanta.CBG.png?v=1747449138',
    'red bull': 'https://img.freepik.com/premium-photo/red-bull-can_925121-7226.jpg',
    'bisleri': 'https://www.bisleri.com/on/demandware.static/-/Library-Sites-RefArchSharedLibrary/default/dw24de3347/images/500ml.png',
    'smirnoff': 'https://www.havenwines.co.ke/wp-content/uploads/2021/08/Smirnoff-Gold-750ml-Vodka.jpg',
    "mcdowell's no.1": 'http://liquor.trendswe.com/wp-content/uploads/2021/12/Mc-Dowells-No.1-Luxury-Premium-Whisky.jpg',
}

PRODUCT_IMAGE_URLS = {
    'kingfisher': 'https://api.mircate.com/5p1hp1d2t/CALL/PIMAPI/getImage/jux9er4tf08?filename=jux9er4tf08-7cf533a774aa43d49ee0766c0617d901.png&quality=100',
    'kingfisher premium beer 650ml': 'https://digitalcontent.api.tesco.com/v2/media/ghs/4f3bebdf-d773-4892-aada-7ac2e7ac7fee/snapshotimagehandler_1389792880.jpeg?h=540&w=540',
    'tuborg': 'http://kaltoggott.is/cdn/shop/files/Classic500.jpg?v=1758314587',
    'budweiser': 'https://www.cantechonline.com/wp-content/uploads/Budweiser-alu-beer-bottle_2014-Fifa-World-cup.jpg',
    'corona': 'https://licoresmaduro.com/wp-content/uploads/2023/10/4860.png',
    'corona special': 'https://licoresmaduro.com/wp-content/uploads/2023/10/4860.png',
    'old monk': 'https://antiquitywhisky.in/wp-content/uploads/2024/08/Old-Monk-rum-price-in-India-Latest-August-Updated-Price-1.webp',
    'bacardi': 'https://alto1994.com/tienda/27924-large_default/ron-bacardi-big-apple-1l-35-12.jpg',
    'bacardi orange': 'https://alto1994.com/tienda/27924-large_default/ron-bacardi-big-apple-1l-35-12.jpg',
    'bacardi lemon': 'https://alto1994.com/tienda/27924-large_default/ron-bacardi-big-apple-1l-35-12.jpg',
    'captain morgan': 'https://images.squarespace-cdn.com/content/v1/5eb05eb2b88ab04655228885/1655630271571-AWDLF2YWZLB82IKFR33O/Captain-Morgan-Tiki-Mango-Pineapple-Rum-The-Rum-Company.jpg',
    'royal stag': 'https://olkeriliquor.com/wp-content/uploads/2023/06/ROYAL-STAG-750ML-WHISKY.jpg',
    'blenders pride': 'https://curlytales.com/wp-content/uploads/2023/09/Blenders-Pride.jpg',
    'jack daniels': 'https://halftimebeverage.com/media/catalog/product/cache/5a9ece781d558937ae51db0fc99c94f4/rdi/rdi/jack-daniels-cherry-lime-46-20485_1.png',
    'coca cola': 'https://www.awesomeinventions.com/wp-content/uploads/2019/11/Coca-Cola-Cinnamon-and-Sprite-Winter-Spiced-Cranberry.jpg',
    'coca cola cranberry': 'https://www.awesomeinventions.com/wp-content/uploads/2019/11/Coca-Cola-Cinnamon-and-Sprite-Winter-Spiced-Cranberry.jpg',
    'pepsi': 'https://products.pepsico.ua/uploads/products/Pepsi_Pineapple_Peach_Beverages_1000.jpg',
    'pepsi peach': 'https://products.pepsico.ua/uploads/products/Pepsi_Pineapple_Peach_Beverages_1000.jpg',
    'sprite': 'https://5.imimg.com/data5/SELLER/Default/2023/3/296218244/ZM/YN/HI/130701409/250ml-sprite-cold-drink-1000x1000.jpg',
    'sprite green': 'https://5.imimg.com/data5/SELLER/Default/2023/3/296218244/ZM/YN/HI/130701409/250ml-sprite-cold-drink-1000x1000.jpg',
    'fanta': 'http://popsnaxworld.com/cdn/shop/files/BlueberryFanta.CBG.png?v=1747449138',
    'fanta berry': 'http://popsnaxworld.com/cdn/shop/files/BlueberryFanta.CBG.png?v=1747449138',
    'red bull': 'https://img.freepik.com/premium-photo/red-bull-can_925121-7226.jpg',
    'red bull premium': 'https://img.freepik.com/premium-photo/red-bull-can_925121-7226.jpg',
    'bisleri': 'https://www.bisleri.com/on/demandware.static/-/Library-Sites-RefArchSharedLibrary/default/dw24de3347/images/500ml.png',
    'bisleri classic': 'https://www.bisleri.com/on/demandware.static/-/Library-Sites-RefArchSharedLibrary/default/dw24de3347/images/500ml.png',
    'smirnoff': 'https://www.havenwines.co.ke/wp-content/uploads/2021/08/Smirnoff-Gold-750ml-Vodka.jpg',
    'smirnoff gold': 'https://www.havenwines.co.ke/wp-content/uploads/2021/08/Smirnoff-Gold-750ml-Vodka.jpg',
    "mcdowell's no.1": 'http://liquor.trendswe.com/wp-content/uploads/2021/12/Mc-Dowells-No.1-Luxury-Premium-Whisky.jpg',
    "mcdowell's no.1 silver": 'http://liquor.trendswe.com/wp-content/uploads/2021/12/Mc-Dowells-No.1-Luxury-Premium-Whisky.jpg',
}

@st.cache_resource
def setup():
    csv_path = CSV_PATH
    try:
        df = pd.read_csv(csv_path, engine='python', quoting=csv.QUOTE_NONE)
    except UnicodeDecodeError:
        encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding, engine='python', quoting=csv.QUOTE_NONE)
                break
            except Exception:
                continue
        if df is None:
            raise ValueError(f"Could not read CSV with any encoding")

    df.columns = df.columns.str.replace('"', '').str.strip()
    for col in ['Product_Name', 'Category', 'Description', 'Image_URL', 'Price', 'Rating', 'Review_Count']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace('"', '', regex=False)

    if 'Image_URL' in df.columns:
        df['Image_URL'] = df['Image_URL'].replace({'nan': DEFAULT_IMAGE, 'None': DEFAULT_IMAGE, '': DEFAULT_IMAGE})
    else:
        df['Image_URL'] = DEFAULT_IMAGE
    if 'Review_Count' in df.columns:
        df['Review_Count'] = pd.to_numeric(df['Review_Count'], errors='coerce').fillna(0).astype(int)
    df['Product_Name'] = df['Product_Name'].fillna('')
    df['Category'] = df['Category'].fillna('')
    df['Description'] = df['Description'].fillna('')

    df['soup'] = df['Product_Name'] + " " + df['Category'] + " " + df['Description']

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['soup'])
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
                      
    return df, similarity_matrix

#load dataset
products_df, similarity_matrix = setup()

# Keep the Image_URL values from the CSV file (white.py.csv).
# If a product is missing an image URL, the default image will be used later.

#from recommenadtion the faction

                      
def get_recommendations(product_name, df, similarity_matrix, num_recommendations=4):
                      try:
                          idx = df[df['Product_Name'] == product_name].index[0]
                          sim_scores = list(enumerate(similarity_matrix[idx]))
                          sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                          sim_scores = sim_scores[1:num_recommendations+1]
                          product_indices = [i[0] for i in sim_scores]
                          return df.iloc[product_indices]
                      except IndexError:
                          return pd.DataFrame()
def get_image_path(image_url):
    img_url = str(image_url or DEFAULT_IMAGE).strip().strip('"')
    if not img_url or img_url.lower() in {'nan', 'none'}:
        return DEFAULT_IMAGE

    if img_url.startswith(('http://', 'https://')):
        candidates = []
        if img_url.startswith('http://'):
            candidates.append('https://' + img_url[7:])
            candidates.append(img_url)
        else:
            candidates.append(img_url)

        for candidate in candidates:
            cache_name = hashlib.md5(candidate.encode('utf-8')).hexdigest() + '.jpg'
            cached_path = IMAGE_CACHE_DIR / cache_name
            if cached_path.exists():
                return str(cached_path)

            try:
                req = Request(candidate, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=20) as response:
                    data = response.read()
                    if not data:
                        continue
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' not in content_type:
                        continue
                    cached_path.write_bytes(data)
                    return str(cached_path)
            except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                continue

        return img_url

    cache_name = hashlib.md5(img_url.encode('utf-8')).hexdigest() + '.jpg'
    cached_path = IMAGE_CACHE_DIR / cache_name
    if cached_path.exists():
        return str(cached_path)

    try:
        req = Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as response:
            data = response.read()
            if not data:
                return DEFAULT_IMAGE
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type:
                return DEFAULT_IMAGE
            cached_path.write_bytes(data)
            return str(cached_path)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return DEFAULT_IMAGE


def get_brand_image_path(brand_name):
    brand = str(brand_name or '').strip()
    if not brand or brand.lower() in {'nan', 'none'}:
        return DEFAULT_IMAGE

    brand_key = brand.lower()
    image_url = None

    for key in BRAND_IMAGE_URLS:
        if key in brand_key:
            image_url = BRAND_IMAGE_URLS[key]
            break

    if not image_url:
        image_url = BRAND_IMAGE_URLS.get(brand_key, DEFAULT_IMAGE)

    return get_image_path(image_url)


def _normalize_text(value):
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').strip().lower()).strip()


def get_product_image_url(product_name, image_url, brand_name):
    product_key = _normalize_text(product_name)
    brand_key = _normalize_text(brand_name)

    for key, mapped_url in sorted(PRODUCT_IMAGE_URLS.items(), key=lambda item: len(item[0]), reverse=True):
        norm_key = _normalize_text(key)
        if not norm_key:
            continue
        if norm_key == product_key or norm_key == brand_key or norm_key in product_key or norm_key in brand_key:
            return mapped_url

    if image_url and str(image_url).strip() and str(image_url).strip().lower() not in {'nan', 'none', ''}:
        return str(image_url).strip().strip('"')

    return None


def show_product_image(image_url, brand_name=None, product_name=None, width=320, use_container_width=True):
    override_url = get_product_image_url(product_name, image_url, brand_name)
    if override_url and str(override_url).strip() and str(override_url).strip().lower() not in {'nan', 'none', ''} and str(override_url).strip() != DEFAULT_IMAGE:
        image_path = get_image_path(override_url)
    elif brand_name and str(brand_name).strip() not in {'nan', 'none', ''}:
        image_path = get_brand_image_path(brand_name)
    else:
        image_path = get_image_path(image_url)
    st.image(image_path, width=width, use_container_width=use_container_width)

#streamlit code
st.subheader("Select a Product:")
all_products = products_df['Product_Name'].tolist()
selected_product=st.selectbox("Search items...",all_products)

if selected_product:
    current_item = products_df[products_df['Product_Name'] == selected_product].iloc[0]
    col1, col2 = st.columns([1.2, 2])
    with col1:
        show_product_image(current_item.get('Image_URL', DEFAULT_IMAGE), brand_name=current_item.get('Brand_Name'), product_name=current_item.get('Product_Name'), width=340)
    with col2:
        st.write(f"###{current_item['Product_Name']}")
        st.write(f"*Brand.* {current_item.get('Brand_Name', 'N/A')}")
        st.write(f"*Price.* {current_item.get('Price', 'N/A')}")
        st.write(f"*Rating.* {current_item.get('Rating', 'N/A')}")
        st.write(f"*Description.* {current_item.get('Description', 'NO description available')}")
        st.write("📱 Order on WhatsApp: 9691058070")

        product_link = None
        for col_name in ['Product_URL', 'URL', 'Link', 'Product_Link', 'Website']:
            if col_name in products_df.columns:
                value = str(current_item.get(col_name, '')).strip()
                if value and value.lower() not in {'nan', 'none', ''}:
                    product_link = value
                    break

        if not product_link:
            product_link = current_item.get('Image_URL', DEFAULT_IMAGE)

        whatsapp_link = "https://wa.me/9691058070"
        st.markdown(f"[📱 Order on WhatsApp]({whatsapp_link})")
        if isinstance(product_link, str) and product_link.startswith(('http://', 'https://')):
            st.markdown(f"[🔗 Open product link]({product_link})")
        st.markdown("---")
          
#from the reviews display
    st.subheader("💬 Customer Reviews for this Products")
    review_col = 'Review_Count' if 'Review_Count' in products_df.columns else 'Review Count'
    if review_col in products_df.columns:
        review_value = pd.to_numeric(current_item[review_col], errors='coerce')
        if pd.isna(review_value):
            review_value = 0
    else:
        review_value = 0
    if review_value > 0:
        with st.container():
            st.write(f"Rating: {current_item.get('Rating', 'N/A')} ⭐ | Top Review")
            st.write("\"Good product quality matches the description well\"")
            st.markdown("<small>Verified Purchase</small>", unsafe_allow_html=True)
    else:
        st.info("Is product ke liye abhi koi reviews nahi hain.")
        st.markdown("---")

    st.subheader("🔥 Customers who viewed this also liked:")
    recommendations = get_recommendations(selected_product, products_df, similarity_matrix)
    if not recommendations.empty:
        cols = st.columns(len(recommendations))
        for i, (idx, rec_item) in enumerate(recommendations.iterrows()):
            with cols[i]:
                show_product_image(rec_item.get('Image_URL', DEFAULT_IMAGE), brand_name=rec_item.get('Brand_Name'), product_name=rec_item.get('Product_Name'), width=260, use_container_width=True)
                short_title = rec_item['Product_Name'][:40] + "..." if len(rec_item['Product_Name']) > 40 else rec_item['Product_Name']
                st.write(f"**{short_title}**")
                st.write(f"Price: {rec_item.get('Price', 'N/A')}")
                                 
          
          
      
        
                                   
                  
    
