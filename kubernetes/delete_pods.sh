#!/bin/bash
for each in $(kubectl get pods --all-namespaces | grep 'Evicted\|Error\|Failed' | awk '{print $1 "/" $2 "/" $4}');
do
  del_args=(${each//\// })
  echo "DELETING ${del_args[0]} ${del_args[1]} ${del_args[2]}"
  kubectl delete pods -n ${del_args[0]} ${del_args[1]} --request-timeout=666
done
