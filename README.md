# P2P-binary-classification

Reference: https://github.com/zhulinn/P2P-File-System-Python/

# IOT example :

Reference: https://cloud.google.com/iot/docs/samples/end-to-end-sample
https://cloud.google.com/iot/docs/quickstart
https://cloud.google.com/docs/authentication/getting-started#command-line



###registry
https://console.cloud.google.com/iot/locations/us-central1/registries/my-registry/overview?folder=&organizationId=&project=e2e-example-277116


### authentication 
https://cloud.google.com/docs/authentication/getting-started#command-line  

```gcloud projects add-iam-policy-binding e2e-example-277116 --member "serviceAccount:ppriyank@e2e-example-277116.iam.gserviceaccount.com" --role "roles/owner"```


### username 
https://console.cloud.google.com/iam-admin/iam?project=e2e-example-277116

### create subscription 
gcloud pubsub subscriptions create \
    projects/e2e-example-277116/subscriptions/my-subscription \
    --topic=projects/e2e-example-277116/topics/my-device-events


### for google authentication 

```export GOOGLE_APPLICATION_CREDENTIALS="/Users/ppriyank/coding/p2p project/chikka.json"```
