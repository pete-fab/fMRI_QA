VERSION = 1.0

build: 
	docker build -t neuromcb/fmri_qa:dev .

pull:
	docker pull neuromcb/fmri_qa:$(VERSION)

push:
	docker push neuromcb/fmri_qa:dev

build_afni:
	docker build -t neuromcb/afni images/afni/

regenerate_afni_dockerfile:
	docker run --rm kaczmarj/neurodocker:0.7.0 generate docker  --base debian:stretch --pkg-manager apt --afni version=latest install_r_pkgs=true install_python2=true --vnc passwd=afni start_at_runtime=true > images/afni/Dockerfile

release:
	docker build -t neuromcb/fmri_qa:$(VERSION) .
	docker push neuromcb/fmri_qa:$(VERSION)