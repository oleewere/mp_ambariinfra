# Ambari Infra Service MPack for Ambari

## Generate Ambari Infra Service mpack tarball
Download mp_ambariinfra repository from git then run:
```bash
cd mp_ambariinfra
./gradlew clean buildTar -Pversion=1.0.0 # additional options: -PmpackName=...
```

## Install  Ambari Infra Service mpack

Stop Ambari Server:
```bash
ambari-server stop
```

Install Solr mpack:
```bash
ambari-server install-mpack --mpack=/my-path/ambari-infra-mpack-1.0.0.tar.gz --verbose
```

Start Ambari Server
```bash
ambari-server start
```
