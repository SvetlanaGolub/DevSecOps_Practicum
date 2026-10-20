```bash
kubectl logs -n falco falco-ck8sw -c falco --since=1m | grep "PetClinic write outside /tmp" | grep "petclinic"

11:06:27.019372590: Warning PetClinic write outside /tmp (file=/dev/shm/falco-test.txt user=petclinic
```