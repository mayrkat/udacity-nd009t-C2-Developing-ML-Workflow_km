### Lambda 1
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['body']['s3_key']
    bucket = event['body']['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    image = '/tmp/image.png'
    s3.download_file(bucket, key, image)
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


### Lambda 2
def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Instantiate a Predictor
    #predictor = Predictor(ENDPOINT)

    # For this model the IdentitySerializer needs to be "image/png"
    #predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    runtime = boto3.Session().client('sagemaker-runtime')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType = 'image/png',Body = image)
    event["inferences"] = json.loads(response['Body'].read().decode('utf-8'))
    #inferences = predictor.predict(image, initial_args={'ContentType': 'image/jpeg'})
    
    # We return the data back to the Step Function    
    #event["inferences"] = inferences
    return {
        'statusCode': 200,
        'body':
            {
            'inferences': event["inferences"]}}


### Lambda 3
import json

THRESHOLD = .93


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['body']['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }