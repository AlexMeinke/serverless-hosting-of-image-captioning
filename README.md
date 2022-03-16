# Serverless ML inference on AWS
Take a deep learning model and host it on AWS, paying only for the inference time that you actually use. The solution uses API Gateway for handling requests from the internet which then get passed to AWS Lambda which in turn loads its code and deep learning model from a docker image that is hosted on AWS Elastic Container Registry.

The model weights and the inference code are taken from [this repository](https://github.com/sgrvinod/a-PyTorch-Tutorial-to-Image-Captioning).
I hope you find this repository useful for serverlessly hosting your own models. Also, see the accompanying [blog post](https://www.alexmeinke.de/2022/03/16/serverless-deploy-image-to-text.html).

I will assume that you have an AWS account and that you have the permissions to use [ECR](https://aws.amazon.com/ecr/), [AWS Lambda](https://aws.amazon.com/lambda/) and [API Gateway](https://aws.amazon.com/api-gateway/).

## Creating the Docker image
First you need to download the [model weights](https://alexm-personal-website-v2.s3.eu-central-1.amazonaws.com/blog/2022-02-01-serverless-deploy-image-to-text/model.pickle) 
and place them into your folder. Then you need to build the docker image

<pre>
docker build -t <b>YOUR-IMAGE-NAME</b> .
</pre>

Next you should create a repository on [ECR](https://aws.amazon.com/ecr/) and note down your AWS region and the prefix for your ECR 
(the first part of your repository's URI). Assuming you have the right credentials configured on your AWS CLI you can run the following command
in order to allow docker to push to your ECR:
<pre>
aws ecr get-login-password --region <b>YOUR-AWS-REGION</b> | docker login --username AWS --password-stdin <b>YOUR-ECR-PREFIX</b>.dkr.ecr.<b>YOUR-AWS-REGION</b>.amazonaws.com
</pre>

Then it's time to actually push to the ECR.
<pre>
docker tag  <b>YOUR-IMAGE-NAME</b>:latest <b>YOUR-ECR-PREFIX</b>.dkr.ecr.<b>YOUR-AWS-REGION</b>.amazonaws.com/<b>YOUR-IMAGE-NAME</b>:latest
docker push <b>YOUR-ECR-PREFIX</b>.dkr.ecr.<b>YOUR-AWS-REGION</b>.amazonaws.com/<b>YOUR-IMAGE-NAME</b>:latest
</pre>

If you hit a snag during any of these steps, also refer to the [documentation](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

## Creating the Lambda Function
Using the docker container from [AWS Lambda](https://aws.amazon.com/lambda/) is easy. During creation in the AWS Management Console, you simply select Container Image as the source. 
After creating the function, don't forget to increase the timeout to at least 35 seconds as during cold starts the model takes a long time to load. 
During warm-starts the latency is on the order of 4-5 seconds for this particular model.

## Creating the API
In order to host the model as an actual API that is accessible from the internet, you can use [API Gateway](https://aws.amazon.com/api-gateway/).
Simply create a method (like a POST method) and selection your Lambda function as the integration enpoint. Also check the box "Use Lambda Proxy integration" in your
method's integration request menu. Finally, you also need to go to settings, "Binary Media Types"and add `image/*`. If you now deploy your model, you should
be able to POST an image and receive a short textual description of its content.
