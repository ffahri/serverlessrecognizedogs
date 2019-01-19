import boto3
from flask import Flask,request,jsonify
from PIL import Image
from twilio.rest import Client 
import io
import uuid
import os
app = Flask(__name__)
client= boto3.client(
    'rekognition',
    aws_access_key_id=os.environ['AWS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_ACCESS_KEY'],
    region_name= 'eu-west-1'
)
account_sid = os.environ['TWILIO_SID'] 
auth_token = os.environ['TWILIO_TOKEN']
twilio = Client(account_sid, auth_token) 
s3 = boto3.client('s3',aws_access_key_id=os.environ['AWS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_ACCESS_KEY'],
    region_name= 'eu-west-1')
s3r = boto3.resource('s3', aws_access_key_id=os.environ['AWS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_ACCESS_KEY'],
    region_name= 'eu-west-1')
bucket_name = 'nesnetanimasunum'
@app.route('/upload', methods=['POST'])
def upload_file():
	img = request.files['image']
	#tt = Image.fromarray(img2)
	imgname=str(uuid.uuid4())
	s3.upload_fileobj(
            img,
            bucket_name,
            imgname,
            ExtraArgs={
                "ContentType": img.content_type
            })
	object_acl = s3r.ObjectAcl(bucket_name,imgname)
	object_acl.put(ACL='public-read')
	
	print("Image detection started")
	response = client.detect_labels(Image={'S3Object': {
            'Bucket': bucket_name,
            'Name': imgname
        }})
	print("Image detection finished.Values sent to client")
	for i in range(len(response['Labels'])):
		if response['Labels'][i]['Name'] == 'Dog' and response['Labels'][i]['Confidence']>90:
			message = twilio.messages.create( 
                              from_='whatsapp:+*******',  
                              body='Köpek fotoğrafı var',      
                              to='whatsapp:+*********',
			      media_url="https://s3-eu-west-1.amazonaws.com/tezdemonesnetanima/"+imgname) 
	return jsonify(Labels=response['Labels'])

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0',port=8080)
