
build: 
	docker build -t mcb/fmri_qa .

build_afni:
	docker build -t mcb/afni images/afni/

regenerate_afni_dockerfile:
	docker run --rm kaczmarj/neurodocker:0.7.0 generate docker  --base debian:stretch --pkg-manager apt --afni version=latest install_r_pkgs=true install_python2=true --vnc passwd=afni start_at_runtime=true > images/afni/Dockerfile