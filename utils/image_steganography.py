from PIL import Image, ImageDraw

def encode_text_to_image(image, text):
    binary_data = ''.join([format(ord(i), '08b') for i in text])
    data_len = len(binary_data)
    img_data = image.getdata()

    new_image_data = []
    highlight_positions = []  # To store the positions of the encoded pixels
    data_index = 0

    for index, pixel in enumerate(img_data):
        new_pixel = list(pixel)
        for i in range(3):  # For RGB
            if data_index < data_len:
                if int(binary_data[data_index]) == 1:
                    highlight_positions.append(index)
                new_pixel[i] = new_pixel[i] & ~1 | int(binary_data[data_index])
                data_index += 1
        new_image_data.append(tuple(new_pixel))

    image.putdata(new_image_data)
    
    # Create a highlighted version of the image
    highlighted_image = highlight_encoded_pixels(image.copy(), highlight_positions)

    return image, highlighted_image

def highlight_encoded_pixels(image, positions):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for pos in positions:
        x = pos % width
        y = pos // width
        draw.rectangle([x, y, x+1, y+1], outline="red")
    return image

def decode_text_from_image(image):
    binary_data = ""
    img_data = image.getdata()
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
    highlighted_image = highlight_encoded_pixels(image.copy(), highlight_positions)
    
    return hidden_text, highlighted_image

def encode_interface(image, text):
    image = image.convert("RGB")  # Ensure image is in RGB mode
    result_image, highlighted_image = encode_text_to_image(image, text + "#####")  # Add end marker
    return result_image, highlighted_image

def decode_interface(image):
    return decode_text_from_image(image)
