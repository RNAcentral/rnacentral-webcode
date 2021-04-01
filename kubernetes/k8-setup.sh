#!/bin/bash
# Script to control access to services using RBAC authorization.
# When executing this script the following items will be created:
# - Namespace
# - ServiceAccount
# - Role
# - RoleBinding

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <path to kubectl config> <namepsace> <data centre prefix>"
    echo "e.g. $0 ~/.kube/myclust.cfg test hx"
    exit 0
fi

CONFIG=$1
NS=$2
DC=$3

echo -e "Using: config file=$CONFIG, namespace=$NS, datacentre=$DC"
sed -e "s/<NAMESPACE>/$NS/g" k8s-setup.tmpl | kubectl --kubeconfig $CONFIG apply -f -
sa_secret=`kubectl get sa $NS-sa -o jsonpath={.secrets[].name} --kubeconfig $CONFIG -n $NS`
kubectl get secret $sa_secret -o go-template='{{index .data "ca.crt"}}' --kubeconfig $CONFIG -n $NS | base64 --decode > "$DC-$NS"-ca.crt
kubectl get secret $sa_secret -o go-template='{{index .data "token"}}' --kubeconfig $CONFIG -n $NS | base64 --decode > "$DC-$NS"-token.txt
echo -e "The following files were created: $DC-$NS-ca.crt and $DC-$NS-token.txt"