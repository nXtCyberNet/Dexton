### ye saar main commands hai list or delete ke liyo varb change to create , (list , watch) for list , stop delete
ya command ko gpt ko de diyo
```
kubectl create role pod-deleter --namespace=bot --verb=delete --resource=pods
kubectl create rolebinding pod-deleter-binding --namespace=bot --role=pod-deleter --serviceaccount=bot:default
```
####is command ko just put karde kaam khatam or maje kar
```
kubectl run (name) --image=asia-south2-docker.pkg.dev/centered-memory-446823-p9/dexton/kbt:latest --port=6969
kubectl expose deployment myapp --type=LoadBalancer --port=6969 --target-port=6969
```
####image push  karne ke baaad

