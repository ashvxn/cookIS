from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import threading
import time

app = Flask(__name__)

# Queue to store frames for display
image_queue = []

def display_image():
    """ Continuously display images from the queue """
    while True:
        if image_queue:
            frame = image_queue.pop(0)

            # Resize the image for better display
            frame = cv2.resize(frame, (800, 600))

            # Display the image with a small delay
            cv2.imshow("Received Image with Text", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.1)

# Start the image display thread
threading.Thread(target=display_image, daemon=True).start()


@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()

    print("Received data:", data)

    text = data.get("text", "No text received")
    image_data = data.get("image")

    if image_data:
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(image_data)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is not None:
                print("✅ Image received successfully!")

                # Add text overlay to the image
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                color = (0, 255, 0)
                thickness = 2
                position = (10, 40)
                cv2.putText(frame, f"Text: {text}", position, font, font_scale, color, thickness, cv2.LINE_AA)

                # Add the image to the queue for display
                image_queue.append(frame)

            else:
                print("❌ Failed to decode image")

        except Exception as e:
            print(f"⚠ Error decoding image: {e}")

    else:
        print("❌ No image received")

    return jsonify({
        "response": f"Text: {text}",
        "image_received": bool(image_data)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)