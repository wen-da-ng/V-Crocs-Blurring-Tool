import os
import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO
from PIL import Image
from io import BytesIO

def load_model(confidence):
    model = YOLO('best.pt')
    model.conf = confidence
    return model

def apply_mosaic(image, top_left, bottom_right, mosaic_size=15):
    (startX, startY) = top_left
    (endX, endY) = bottom_right
    roi = image[startY:endY, startX:endX]
    if roi.size == 0:
        return image

    for x in range(0, roi.shape[1], mosaic_size):
        for y in range(0, roi.shape[0], mosaic_size):
            sub_roi = roi[y:y + mosaic_size, x:x + mosaic_size]
            color = np.mean(sub_roi, axis=(0, 1), dtype=int)
            roi[y:y + mosaic_size, x:x + mosaic_size] = color
    image[startY:endY, startX:endX] = roi
    return image

def run_detection(model, img_data, class_id):
    img_arrays = [cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR) for data in img_data]
    results = model(img_arrays)
    modified_images = []
    for img_array, result in zip(img_arrays, results):
        if result.boxes and len(result.boxes) > 0:
            for box in result.boxes:
                if box.cls.item() == class_id and box.conf.item() >= model.conf:
                   
                    if box.xyxy.shape[1] == 4: 
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy() 
                        top_left = (int(x1), int(y1))
                        bottom_right = (int(x2), int(y2))
                        print(f"Applying mosaic to: {top_left} to {bottom_right}") 
                        img_array = apply_mosaic(img_array, top_left, bottom_right)
        is_success, buffer = cv2.imencode(".jpg", img_array)
        io_buf = BytesIO(buffer)
        modified_images.append(io_buf)
    return modified_images

st.title('ViTrox Crocs Bluring Tool')

confidence_level = st.slider("Select the confidence level:", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
class_options = {0: 'ViTrox Crocs', 1: 'Non-ViTrox Shoes'}
selected_class = st.selectbox('Select Class to Detect:', options=list(class_options.keys()), format_func=lambda x: class_options[x])

uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    img_data = [img.read() for img in uploaded_files]

    st.subheader("Uploaded Images")
    cols = st.columns(len(uploaded_files))
    for col, img, data in zip(cols, uploaded_files, img_data):
        img_array = np.array(Image.open(BytesIO(data)))
        col.image(img_array, width=100, caption=img.name, use_column_width=True)

    if st.button('Run Detection with Mosaic Blur'):
        if img_data:
            model = load_model(confidence_level)
            modified_images = run_detection(model, img_data, selected_class)
            for i, modified_image in enumerate(modified_images):
                st.image(modified_image, caption=f'Result for image {i}', use_column_width=True)
                st.download_button(
                    label=f"Download Result {i}",
                    data=modified_image,
                    file_name=f'mosaic_blur_{i}.jpg',
                    mime="image/jpeg"
                )
            st.success('Detection complete! You can download the results using the buttons above.')
        else:
            st.error("Please upload at least one image.")
