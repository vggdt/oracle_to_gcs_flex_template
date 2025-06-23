# oracle_to_gcs_flex_template
Sample Python Flex Template for send data from Oracle (JDBC) to GCS

# Submit
gcloud builds submit . --tag us-central1-docker.pkg.dev/{project]/dataflow-images/oracle_to_gcs:v1 --project {project}  

# Build
gcloud dataflow flex-template build gs://{yourbucket}/folder/oracle_to_gcs.json --image "us-central1-docker.pkg.dev/{project}/dataflow-images/oracle_to_gcs:v1"  --sdk-language "PYTHON" --metadata-file=metadata.json  --project {project}

# Test
gcloud dataflow flex-template run "flex-v4" --template-file-gcs-location=gs://us-central1-composer-dev-co-2570abd9-bucket/plugins/oracle_to_gcs.json  --region=us-central1 --project={project} --subnetwork=https://www.googleapis.com/compute/v1/projects/{project}/regions/us-central1/subnetworks/{subnet}  --parameters="connection_url=jdbc:oracle:thin:@//url_or_ip:1521/DWP,username={username},password={password},query=SELECT * FROM table,output_path=gs://{yourbucket}/folder/sub_folder/snapshots/" 
