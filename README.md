# P2P-binary-classification

Reference: https://github.com/zhulinn/P2P-File-System-Python/

#Azure
# IOT example :

### Hub creation 
https://docs.microsoft.com/en-us/azure/iot-hub/quickstart-send-telemetry-python


https://docs.microsoft.com/en-us/azure/iot-hub/quickstart-send-telemetry-python



# Google
# IOT example :

Reference: https://cloud.google.com/iot/docs/samples/end-to-end-sample
https://cloud.google.com/iot/docs/quickstart
https://cloud.google.com/docs/authentication/getting-started#command-line

##Example:

```cloud_iot/python-docs-samples/iot/api-client/end_to_end_example```


### Topic
https://console.cloud.google.com/cloudpubsub/topic/list?project=e2e-example-277116

###registry
https://console.cloud.google.com/iot/locations/us-central1/registries/my-registry/overview?folder=&organizationId=&project=e2e-example-277116

###Devices


https://cloud.google.com/iot/docs/how-tos/devices  

https://console.cloud.google.com/iot/registries?_ga=2.112919940.1009158978.1589306999-361084232.1589306999&_gac=1.12117702.1589403961.CjwKCAjwte71BRBCEiwAU_V9h6rPPtzNKV960vW_ABvYyVLIk_Vjsyzi_-ldLJReeAdhoXDU_xdv3hoCQMUQAvD_BwE&project=e2e-example-277116&folder=&organizationId=

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


## Trouble shooting : 

https://cloud.google.com/iot/docs/support/troubleshooting


<!-- client throws unresolved error while and sending message  disconnected: 1: Out of memory. -->




