from moviepy.editor import VideoFileClip
from PIL import Image, ImageDraw
import numpy as np

# Function to encode text into a video and return a highlighted frame separately
def encode_text_to_video(video_path, text):
    video = VideoFileClip(video_path)
    binary_data = ''.join([format(ord(i), '08b') for i in text])
    data_len = len(binary_data)
    data_index = 0
    highlighted_frame = None
    
    def process_frame(frame):
        nonlocal data_index, highlighted_frame
        img = Image.fromarray(frame)
        img_data = img.getdata()

        new_image_data = []
        highlight_positions = []  # Store positions of encoded pixels

        for index, pixel in enumerate(img_data):
            new_pixel = list(pixel)
            for i in range(3):  # For RGB
                if data_index < data_len:
                    if int(binary_data[data_index]) == 1:
                        highlight_positions.append(index)
                    new_pixel[i] = new_pixel[i] & ~1 | int(binary_data[data_index])
                    data_index += 1
            new_image_data.append(tuple(new_pixel))

        img.putdata(new_image_data)
        
        # Generate the highlighted frame for the first frame
        if highlighted_frame is None:
            highlighted_frame = highlight_encoded_pixels(img.copy(), highlight_positions)

        return np.array(img)

    new_video = video.fl_image(process_frame)
    output_video_path = "stego_video.mp4"
    new_video.write_videofile(output_video_path, codec="libx264")
    
    # Save the highlighted frame as an image
    if highlighted_frame:
        highlighted_frame_path = "highlighted_frame.png"
        highlighted_frame.save(highlighted_frame_path)
        return output_video_path, highlighted_frame_path
    else:
        return output_video_path, None

def highlight_encoded_pixels(image, positions):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for pos in positions:
        x = pos % width
        y = pos // width
        draw.rectangle([x, y, x+1, y+1], outline="red")
    return image

# Function to decode text from the first frame of a video
def decode_text_from_video(video_path):
    video = VideoFileClip(video_path)
    first_frame = video.get_frame(0)  # Get the first frame at time = 0
    img = Image.fromarray(first_frame)
    binary_data = ""
    img_data = img.getdata()
    highlight_positions = []

    for index, pixel in enumerate(img_data):
        for i in range(3):  # For RGB
            binary_data += bin(pixel[i])[-1]
            if bin(pixel[i])[-1] == '1':
                highlight_positions.append(index)
    
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "#####":  # 종료 마커를 찾으면
            break
    
    # 종료 마커를 기준으로 텍스트 분리
    hidden_text = decoded_data.split("#####")[0] if "#####" in decoded_data else "No hidden text found"
    
    # 하이라이트된 이미지 생성
    highlighted_image = highlight_encoded_pixels(img.copy(), highlight_positions)
    
    return hidden_text, highlighted_image
