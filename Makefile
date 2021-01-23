VERSION = 1.1

build: 
	docker build -t neuromcb/fmri_qa:dev .
	docker build -t neuromcb/fmri_qa:latest .

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

build_filter_copy:
	docker build -t neuromcb/fmri_qa:dev .
	docker build -t neuromcb/fmri_qa:latest .
	docker build --build-arg version=dev -t neuromcb/filter_copy:dev images/filter_copy
	docker build --build-arg version=latest -t neuromcb/filter_copy:latest images/filter_copy

push_filter_copy:
	docker push neuromcb/filter_copy:dev


release_filter_copy:
	docker build -t neuromcb/fmri_qa:$(VERSION) .
	docker build --build-arg version=$(VERSION) -t neuromcb/filter_copy:$(VERSION) images/filter_copy
	docker push neuromcb/filter_copy:$(VERSION)