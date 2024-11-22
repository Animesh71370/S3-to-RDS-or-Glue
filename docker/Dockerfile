# Use the AWS Lambda Python image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy the application code and requirements file from the app folder
COPY app/app.py ${LAMBDA_TASK_ROOT}/app.py
COPY app/requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the CMD to your handler function
CMD ["app.lambda_handler"]
