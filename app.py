import json
import joblib
from PIL import Image, ImageOps
import io
import base64


model_file_name = "model.pickle"
loaded_model = joblib.load(model_file_name)


def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
    }
    
    
    if len(event['body'])==2:
        return {
            'headers' : headers,
            'statusCode': 204,
            'body': json.dumps({
                "message": "Model is now preloaded"
            }),
        }
    
    uploaded_file = base64.b64decode(event['body'])
    img = Image.open(io.BytesIO(uploaded_file))
    img = ImageOps.exif_transpose(img)
    
    seq, alphas = loaded_model.predict(img)
    response = ' '.join([loaded_model.rev_word_map[s] for s in seq][1:-1])
    print(response)
    
    return {
        'headers' : headers,
        'statusCode': 200,
        'body': json.dumps({
            "message": response
        }),
    }
