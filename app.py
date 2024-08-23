import gradio as gr
from utils.image_steganography import encode_interface, decode_interface
from utils.video_steganography import encode_text_to_video, decode_text_from_video
from moviepy.editor import VideoFileClip
from PIL import Image

# Function to encode the same text multiple times into an image
def save_and_preview_encoded_images(image_files, text, text_count):
    encoded_images = []
    highlighted_images = []
    output_paths = []
    full_text = (text + " ") * text_count
    for i, file_path in enumerate(image_files):
        image = Image.open(file_path)
        result_image, highlighted_image = encode_interface(image, full_text + "#####")
        output_path = f"encoded_image_{i+1}.png"
        highlighted_path = f"highlighted_image_{i+1}.png"
        result_image.save(output_path)
        highlighted_image.save(highlighted_path)
        encoded_images.append(result_image)
        highlighted_images.append(highlighted_image)
        output_paths.append(output_path)
    return encoded_images, highlighted_images, gr.update(visible=True, value=output_paths)

# Function to encode the same text multiple times into a video
def save_and_preview_encoded_videos(video_files, text, text_count):
    output_paths = []
    highlighted_frames = []
    full_text = (text + " ") * text_count
    for i, video_file_path in enumerate(video_files):
        video_path, highlighted_frame_path = encode_text_to_video(video_file_path, full_text + "#####")
        output_paths.append(video_path)
        if highlighted_frame_path:
            highlighted_frames.append(highlighted_frame_path)
    return gr.update(visible=True, value=output_paths), gr.Gallery(value=highlighted_frames)

# Function to decode text from the first frame of a video
def decode_video_first_frame(video):
    video_clip = VideoFileClip(video)  # Use video directly as it is a file path
    first_frame = video_clip.get_frame(0)  # Get the first frame (time = 0)
    image = Image.fromarray(first_frame)  # Convert to PIL Image
    hidden_text, highlighted_image = decode_interface(image)
    return hidden_text, highlighted_image

# Function to decode text from an image
def decode_image(image):
    hidden_text, highlighted_image = decode_interface(image)
    return hidden_text, highlighted_image

# Gradio Interface for Encoding the same text into multiple images
encode_image_interface = gr.Interface(
    fn=save_and_preview_encoded_images,
    inputs=[
        gr.Files(label="Upload Images", type="filepath", file_count="multiple", file_types=["image"]),
        gr.Textbox(label="Enter text to encode"),
        gr.Slider(label="Number of times to encode text", minimum=1, maximum=10, step=1, value=1)
    ],
    outputs=[
        gr.Gallery(label="Preview Encoded Images"),
        gr.Gallery(label="Preview Highlighted Images"),
        gr.File(label="Download Encoded Images")
    ],
    title="Encode Text into Multiple Images"
)

# Gradio Interface for Encoding the same text into multiple videos
encode_video_interface = gr.Interface(
    fn=save_and_preview_encoded_videos,
    inputs=[
        gr.Files(label="Upload Videos", type="filepath", file_count="multiple", file_types=["video"]),
        gr.Textbox(label="Enter text to encode"),
        gr.Slider(label="Number of times to encode text", minimum=1, maximum=10, step=1, value=1)
    ],
    outputs=[
        gr.Files(label="Download Encoded Videos", visible=False),
        gr.Gallery(label="Preview Highlighted Frames")  # Show highlighted frames
    ],
    title="Encode Text into Multiple Videos"
)

# Gradio Interface for Decoding Text from Images
decode_image_interface = gr.Interface(
    fn=decode_image,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=[gr.Textbox(label="Decoded Text"), gr.Image(label="Highlighted Image")],
    title="Decode Text from Image"
)

# Gradio Interface for Decoding Text from the First Frame of a Video
decode_video_interface = gr.Interface(
    fn=decode_video_first_frame,
    inputs=gr.Video(label="Upload Video"),
    outputs=[gr.Textbox(label="Decoded Text"), gr.Image(label="Highlighted Frame")],
    title="Decode Text from Video (First Frame)"
)

# Combine interfaces into a tabbed interface
app = gr.TabbedInterface(
    interface_list=[encode_image_interface, decode_image_interface, encode_video_interface, decode_video_interface],
    tab_names=["Encode Text into Images", "Decode Text from Images", "Encode Text into Videos", "Decode Text from Videos"]
)

# Launch the Gradio app
app.launch()
