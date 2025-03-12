from flask import Flask ,request,send_file
from flask_cors import CORS
import cv2
import numpy as np 
import io

app=Flask(__name__)
CORS(app)

def cartoonify(image):

    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray=cv2.medianBlur(gray,5)
    edges=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,9,9)

    color=cv2.bilateralFilter(image,9,250,250)

    cartoon=cv2.bitwise_and(color,color,mask=edges)

    return cartoon


    @app.route('/cartoonify',methods=['POST'])

    def cartoonify_image():

        if 'image' not in request.file:
            return "NO file provided",400

        file=request.file['image']

        file_bytes=np.fromstring(file.read(),np.uint8)

        image=cv2.imdecode(file_bytes,cv2.IMREAD_COLOR)

        cartoon=cartoonify(image)


        ret, buffer = cv2.imencode('.jpg', cartoon)
    io_buf = io.BytesIO(buffer)
    
    
    return send_file(io_buf, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)