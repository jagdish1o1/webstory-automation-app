import streamlit as st
import boto3
import json

# Secrets picked from env
access_key = st.secrets["access_key"]
secret_key = st.secrets["secret_key"]
state_machine_arn = st.secrets["state_machine_arn"]

# Initialize boto3 client
client = boto3.client('stepfunctions',aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-east-1')
sqs_client = boto3.client('sqs', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-east-1')
sqs_queue_url = st.secrets["sqs_queue_url"]  # Add your SQS queue URL to your secrets

# Initialize session state for site details
if "site_details" not in st.session_state:
    st.session_state["site_details"] = []

# Sidebar for site details
st.sidebar.title("Site Details")
site_keys = ["host", "username", "password"]
new_site = {}
for key in site_keys:
    new_site[key] = st.sidebar.text_input(f"Enter {key}", value="")

if st.sidebar.button("Add Site"):
    st.session_state["site_details"].append(new_site)

# Main screen for URLs and site selection
st.title("Story URLs")
story_urls = st.text_area("Enter story URLs (one per line, up to 50)", height=300)
story_urls = story_urls.split("\n")  # Limit to 100 URLs

# Site selection
st.title("Select Site")
site_options = [site['host'] for site in st.session_state["site_details"]]
selected_site = st.selectbox("Choose a site", options=site_options)

# Select Method
st.title("Select Method")
selected_method = st.selectbox("Choose a method", options=['Queue', 'Direct'])

if st.button("Submit"):
    selected_site_index = site_options.index(selected_site)
    selected_site = st.session_state["site_details"][selected_site_index]
    for url in story_urls:
        input_payload = {
            "site": selected_site
        }
        if url.startswith('https://') or url.startswith('http://'):
            input_payload.update({
                "url": url,
                "story_type": "url"
            })
        else:
            input_payload.update({
                "keyword": url,
                "story_type": "keyword"
            })

        if selected_method.lower() == "direct":
            # Start an execution
            response = client.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps(input_payload)
            )
    
        if selected_method.lower() == "queue":
            # Send a message to sqs queue
            response = sqs_client.send_message(
                QueueUrl=sqs_queue_url,
                MessageBody=json.dumps(input_payload)
            )


    st.success(f"All URLs sent to {selected_method} successfully!")
