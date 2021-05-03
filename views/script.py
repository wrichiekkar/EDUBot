import io
import os
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import pandas as pd
from pdf2image import convert_from_path
import export
import json


def runScript():

    #Getting JSON data from all_output.json
    with open('output/all_output.json') as f:
            canvas_data = json.load(f)[0]
        # print(canvas_data)

    #Converting PDF to JPEG

    lectureName = canvas_data['modules'][0]['items'][0]['title']
    lectureUpdateName = lectureName.replace('.pdf','.JPEG')
    lectureTextName = lectureName.replace('.pdf','')
    courseName = canvas_data['name']
    pdfPath = 'output/Default Term/'+ courseName +'/files/' + lectureName
    pages = convert_from_path(pdfPath, 500)

    imageNames = []

    pageCount = 1
    for page in pages:
        imageNames.append(str(pageCount)+lectureUpdateName)
        page.save('LectureImages/'+str(pageCount)+lectureUpdateName, 'JPEG')
        pageCount+=1
        if pageCount == 5:
            break
        
    #Set the os GCP APP Variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'ruhacks2021-uw9e-e3630c9c1cc7.json'

    #client for image annotate vision
    client = vision_v1.ImageAnnotatorClient()

    newFileName = "LectureText/" + courseName + "_" + lectureTextName + ".txt"
    text_file = open(newFileName, "w")

    for name in imageNames:
        
        file_name = os.path.abspath('LectureImages/' + name)

        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        # construct an iamge instance
        image = vision_v1.types.Image(content=content)

        # annotate Image Response
        response = client.text_detection(image=image)  # returns TextAnnotation
        df = pd.DataFrame(columns=['locale', 'description'])

        texts = response.text_annotations
        for text in texts:
            df = df.append(
                dict(
                    locale=text.locale,
                    description=text.description
                ),
                ignore_index=True
            )

        
        text_file.write(df['description'][0])
        text_file.write("")

        print(df['description'][0])
        
        #if keyWord in df['description'][0]:
        #   print("ITS HERE NEEL")

    text_file.close()

