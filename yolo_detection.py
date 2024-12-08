from ultralytics import YOLO
from flask import request, Flask, jsonify
from waitress import serve
from PIL import Image

app = Flask(__name__)

@app.route("/")
def root():
    """
    Site main page handler function.
    :return: Content of index.html file
    """
    with open("index_yolo.html") as file:
        return file.read()


@app.route("/detect", methods=["POST"])
def detect():
    """
    Handler of /detect POST endpoint
    Receives uploaded file with a name "image_file", passes it
    through the selected YOLOv8 model and returns an array
    of bounding boxes.
    :return: a JSON array of objects bounding boxes in format [[x1,y1,x2,y2,object_type,probability],..]
    """
    buf = request.files["image_file"]
    model_name = request.form.get("model", "yolov8m.pt")  # Default to 'yolov8m.pt' if not specified
    boxes = detect_objects_on_image(buf.stream, model_name)
    return jsonify(boxes)


def detect_objects_on_image(buf, model_name):
    """
    Function receives an image,
    passes it through the specified YOLOv8 neural network
    and returns an array of detected objects
    and their bounding boxes
    :param buf: Input image file stream
    :param model_name: The model name to use for detection
    :return: Array of bounding boxes in format [[x1,y1,x2,y2,object_type,probability],..]
    """
    model = YOLO(model_name)  # Load the selected model
    results = model.predict(Image.open(buf))
    result = results[0]
    output = []
    for box in result.boxes:
        x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]

        class_id = box.cls[0].item()

        prob = round(box.conf[0].item(), 2)

        output.append([x1, y1, x2, y2, result.names[class_id], prob])


    return output


if __name__ == "__main__":   
    serve(app, host='0.0.0.0', port=8080)
